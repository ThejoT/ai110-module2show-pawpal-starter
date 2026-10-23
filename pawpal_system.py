"""PawPal+ logic layer: Task, Pet, Owner and Scheduler classes."""

import json
from dataclasses import asdict, dataclass, field, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

VALID_FREQUENCIES = ("once", "daily", "weekly")
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


# --------------------------------------------------------------------------- #
# Task
# --------------------------------------------------------------------------- #
@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding or medication."""

    description: str
    time: str                      # "HH:MM", 24-hour clock
    frequency: str = "once"        # "once", "daily" or "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    priority: str = "medium"       # "low", "medium" or "high"
    duration_minutes: int = 15
    pet_name: str = ""             # filled in by Pet.add_task

    def __post_init__(self) -> None:
        """Validate the time, frequency and priority values."""
        hours, minutes = self.time.split(":")
        if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
            raise ValueError(f"Invalid time '{self.time}', expected HH:MM")
        self.time = f"{int(hours):02d}:{int(minutes):02d}"
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {tuple(PRIORITY_RANK)}")

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task done and return the next occurrence if it recurs."""
        self.completed = True
        if self.frequency == "daily":
            return replace(self, due_date=self.due_date + timedelta(days=1), completed=False)
        if self.frequency == "weekly":
            return replace(self, due_date=self.due_date + timedelta(weeks=1), completed=False)
        return None

    def __str__(self) -> str:
        """Return a one-line, human-readable summary of the task."""
        status = "✅" if self.completed else "⬜"
        return (f"{status} {self.due_date:%a %m/%d} {self.time}  {self.description:<18} "
                f"[{self.pet_name}] ({self.frequency}, {self.priority})")


# --------------------------------------------------------------------------- #
# Pet
# --------------------------------------------------------------------------- #
@dataclass
class Pet:
    """A pet and the list of care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return all of this pet's tasks."""
        return list(self.tasks)

    def task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


# --------------------------------------------------------------------------- #
# Owner
# --------------------------------------------------------------------------- #
class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str):
        """Create an owner with no pets."""
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet, rejecting duplicate names."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"A pet named '{pet.name}' already exists")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name (case-insensitive), or return None."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    # ----- persistence ------------------------------------------------------ #
    def to_dict(self) -> dict:
        """Convert the owner, pets and tasks into plain JSON-friendly data."""
        return {
            "name": self.name,
            "pets": [
                {
                    "name": pet.name,
                    "species": pet.species,
                    "age": pet.age,
                    "tasks": [
                        {**asdict(task), "due_date": task.due_date.isoformat()}
                        for task in pet.tasks
                    ],
                }
                for pet in self.pets
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an Owner (with pets and tasks) from data made by to_dict()."""
        owner = cls(data["name"])
        for pet_data in data.get("pets", []):
            pet = Pet(pet_data["name"], pet_data["species"], pet_data.get("age", 0))
            for task_data in pet_data.get("tasks", []):
                task_data = dict(task_data)
                task_data["due_date"] = date.fromisoformat(task_data["due_date"])
                pet.add_task(Task(**task_data))
            owner.add_pet(pet)
        return owner

    def save_to_json(self, path: str = "data.json") -> None:
        """Save the owner, pets and tasks to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> Optional["Owner"]:
        """Load an owner from a JSON file, or return None if the file doesn't exist."""
        file = Path(path)
        if not file.exists():
            return None
        return cls.from_dict(json.loads(file.read_text(encoding="utf-8")))


# --------------------------------------------------------------------------- #
# Scheduler
# --------------------------------------------------------------------------- #
class Scheduler:
    """The 'brain' that organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Create a scheduler that reads tasks from the given owner."""
        self.owner = owner

    # ----- retrieval -------------------------------------------------------- #
    def get_todays_schedule(self, day: Optional[date] = None) -> List[Task]:
        """Return tasks due on the given day (default today), sorted by time."""
        day = day or date.today()
        todays = [t for t in self.owner.get_all_tasks() if t.due_date == day]
        return self.sort_by_time(todays)

    # ----- sorting ---------------------------------------------------------- #
    @staticmethod
    def sort_by_time(tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by date, then by HH:MM time."""
        # Times are zero-padded "HH:MM", so string order matches clock order.
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    @staticmethod
    def sort_by_priority(tasks: List[Task]) -> List[Task]:
        """Return tasks ordered by priority (high first), then by time."""
        return sorted(tasks, key=lambda t: (PRIORITY_RANK[t.priority], t.due_date, t.time))

    # ----- filtering -------------------------------------------------------- #
    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[Task]:
        """Return tasks matching a pet name and/or completion status, sorted by time."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return self.sort_by_time(tasks)

    # ----- recurring tasks -------------------------------------------------- #
    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task and, if it recurs, add the next occurrence to its pet."""
        next_task = task.mark_complete()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    # ----- conflict detection ----------------------------------------------- #
    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Return warning messages for unfinished tasks sharing the same date and time."""
        tasks = tasks if tasks is not None else self.owner.get_all_tasks()
        slots: Dict[tuple, List[Task]] = {}
        for task in tasks:
            if not task.completed:
                slots.setdefault((task.due_date, task.time), []).append(task)

        warnings = []
        for (day, time), group in sorted(slots.items()):
            if len(group) > 1:
                names = ", ".join(f"{t.description} ({t.pet_name})" for t in group)
                warnings.append(f"⚠️ Conflict on {day} at {time}: {names}")
        return warnings

    # ----- next available slot ---------------------------------------------- #
    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert "HH:MM" into minutes after midnight."""
        hours, minutes = hhmm.split(":")
        return int(hours) * 60 + int(minutes)

    @staticmethod
    def _to_hhmm(total_minutes: int) -> str:
        """Convert minutes after midnight into "HH:MM"."""
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

    def find_next_available_slot(self, duration_minutes: int, day: Optional[date] = None,
                                 day_start: str = "07:00",
                                 day_end: str = "21:00") -> Optional[str]:
        """Return the earliest "HH:MM" start time on a day with no overlapping tasks.

        Unfinished tasks across all pets block time from their start for
        duration_minutes. Returns None if nothing fits between day_start and day_end.
        """
        day = day or date.today()
        busy = sorted(
            (self._to_minutes(t.time), self._to_minutes(t.time) + t.duration_minutes)
            for t in self.owner.get_all_tasks()
            if t.due_date == day and not t.completed
        )

        candidate = self._to_minutes(day_start)
        for start, end in busy:
            if candidate + duration_minutes <= start:
                break                      # the gap before this task is big enough
            candidate = max(candidate, end)

        if candidate + duration_minutes <= self._to_minutes(day_end):
            return self._to_hhmm(candidate)
        return None
