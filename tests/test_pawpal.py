"""Automated tests for the PawPal+ logic layer."""

import os
import sys
from datetime import date, timedelta

import pytest

# Make pawpal_system importable when running `python -m pytest` from the repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Owner, Pet, Scheduler, Task  # noqa: E402


@pytest.fixture
def owner():
    """An owner with two pets and no tasks."""
    o = Owner("Jordan")
    o.add_pet(Pet("Mochi", "dog"))
    o.add_pet(Pet("Luna", "cat"))
    return o


# ----- Phase 2: basic behavior ---------------------------------------------- #
def test_mark_complete_changes_status():
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "08:00"))
    assert pet.task_count() == 1
    assert pet.tasks[0].pet_name == "Mochi"


# ----- Multi-pet access ----------------------------------------------------- #
def test_owner_get_all_tasks_combines_pets(owner):
    owner.get_pet("Mochi").add_task(Task("Walk", "08:00"))
    owner.get_pet("Luna").add_task(Task("Feed", "09:00"))
    assert len(owner.get_all_tasks()) == 2


def test_duplicate_pet_name_rejected(owner):
    with pytest.raises(ValueError):
        owner.add_pet(Pet("mochi", "dog"))


# ----- Sorting -------------------------------------------------------------- #
def test_sort_by_time_is_chronological(owner):
    mochi = owner.get_pet("Mochi")
    for t in ["18:30", "07:00", "12:15", "09:45"]:
        mochi.add_task(Task(f"Task {t}", t))
    times = [t.time for t in Scheduler(owner).get_todays_schedule()]
    assert times == ["07:00", "09:45", "12:15", "18:30"]


def test_single_digit_hour_sorts_correctly(owner):
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Late", "10:00"))
    mochi.add_task(Task("Early", "9:00"))   # normalized to "09:00"
    times = [t.time for t in Scheduler(owner).get_todays_schedule()]
    assert times == ["09:00", "10:00"]


def test_sort_by_priority_then_time():
    tasks = [Task("A", "08:00", priority="low"),
             Task("B", "10:00", priority="high"),
             Task("C", "07:00", priority="high")]
    assert [t.description for t in Scheduler.sort_by_priority(tasks)] == ["C", "B", "A"]


def test_pet_with_no_tasks_gives_empty_schedule(owner):
    assert Scheduler(owner).get_todays_schedule() == []


# ----- Filtering ------------------------------------------------------------ #
def test_filter_by_pet_and_status(owner):
    owner.get_pet("Mochi").add_task(Task("Walk", "08:00"))
    done = Task("Feed", "09:00")
    owner.get_pet("Luna").add_task(done)
    done.mark_complete()

    scheduler = Scheduler(owner)
    assert [t.description for t in scheduler.filter_tasks(pet_name="luna")] == ["Feed"]
    assert [t.description for t in scheduler.filter_tasks(completed=False)] == ["Walk"]
    assert [t.description for t in scheduler.filter_tasks(completed=True)] == ["Feed"]


# ----- Recurrence ----------------------------------------------------------- #
def test_daily_task_creates_next_day_task(owner):
    mochi = owner.get_pet("Mochi")
    today = date.today()
    walk = Task("Walk", "08:00", frequency="daily", due_date=today)
    mochi.add_task(walk)

    next_task = Scheduler(owner).mark_task_complete(walk)

    assert walk.completed is True
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert mochi.task_count() == 2


def test_weekly_task_creates_task_one_week_later(owner):
    luna = owner.get_pet("Luna")
    meds = Task("Meds", "09:00", frequency="weekly", due_date=date(2026, 1, 1))
    luna.add_task(meds)
    next_task = Scheduler(owner).mark_task_complete(meds)
    assert next_task.due_date == date(2026, 1, 8)


def test_one_time_task_does_not_recur(owner):
    mochi = owner.get_pet("Mochi")
    vet = Task("Vet", "14:00")
    mochi.add_task(vet)
    assert Scheduler(owner).mark_task_complete(vet) is None
    assert mochi.task_count() == 1


# ----- Conflict detection --------------------------------------------------- #
def test_conflict_detected_for_same_time_across_pets(owner):
    owner.get_pet("Mochi").add_task(Task("Walk", "08:00"))
    owner.get_pet("Luna").add_task(Task("Feed", "08:00"))
    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_no_conflict_for_different_times(owner):
    owner.get_pet("Mochi").add_task(Task("Walk", "08:00"))
    owner.get_pet("Luna").add_task(Task("Feed", "08:30"))
    assert Scheduler(owner).detect_conflicts() == []


def test_completed_tasks_do_not_conflict(owner):
    walk = Task("Walk", "08:00")
    owner.get_pet("Mochi").add_task(walk)
    owner.get_pet("Luna").add_task(Task("Feed", "08:00"))
    walk.mark_complete()
    assert Scheduler(owner).detect_conflicts() == []


# ----- Validation ----------------------------------------------------------- #
@pytest.mark.parametrize("bad_time", ["25:00", "12:60"])
def test_invalid_time_rejected(bad_time):
    with pytest.raises(ValueError):
        Task("Bad", bad_time)


# ----- Stretch: next available slot ----------------------------------------- #
def test_next_slot_is_day_start_when_schedule_is_empty(owner):
    assert Scheduler(owner).find_next_available_slot(30) == "07:00"


def test_next_slot_skips_busy_tasks_across_pets(owner):
    owner.get_pet("Mochi").add_task(Task("Walk", "07:00", duration_minutes=30))
    owner.get_pet("Luna").add_task(Task("Feed", "07:30", duration_minutes=15))
    # 07:00-07:30 and 07:30-07:45 are busy, so the first free 20 minutes start at 07:45
    assert Scheduler(owner).find_next_available_slot(20) == "07:45"


def test_next_slot_uses_a_gap_that_is_big_enough(owner):
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Walk", "07:00", duration_minutes=30))
    mochi.add_task(Task("Vet", "09:00", duration_minutes=60))
    scheduler = Scheduler(owner)
    assert scheduler.find_next_available_slot(60) == "07:30"   # fits 07:30-08:30
    assert scheduler.find_next_available_slot(120) == "10:00"  # gap is only 90 min


def test_completed_tasks_do_not_block_slots(owner):
    walk = Task("Walk", "07:00", duration_minutes=30)
    owner.get_pet("Mochi").add_task(walk)
    walk.mark_complete()
    assert Scheduler(owner).find_next_available_slot(30) == "07:00"


def test_no_slot_when_day_is_full(owner):
    owner.get_pet("Mochi").add_task(Task("All day", "07:00", duration_minutes=840))
    assert Scheduler(owner).find_next_available_slot(15) is None


# ----- Stretch: JSON persistence -------------------------------------------- #
def test_save_and_load_round_trip(owner, tmp_path):
    owner.get_pet("Mochi").add_task(
        Task("Walk", "08:00", frequency="daily", priority="high",
             due_date=date(2026, 3, 1), duration_minutes=30))
    path = tmp_path / "data.json"
    owner.save_to_json(path)

    loaded = Owner.load_from_json(path)
    assert loaded.name == "Jordan"
    assert [p.name for p in loaded.pets] == ["Mochi", "Luna"]
    task = loaded.get_pet("Mochi").tasks[0]
    assert (task.description, task.time, task.frequency, task.priority) == \
        ("Walk", "08:00", "daily", "high")
    assert task.due_date == date(2026, 3, 1)
    assert task.pet_name == "Mochi"


def test_load_missing_file_returns_none(tmp_path):
    assert Owner.load_from_json(tmp_path / "missing.json") is None
