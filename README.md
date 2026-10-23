# 🐾 PawPal+

PawPal+ is a smart pet care planner for busy owners. It tracks daily routines (feedings, walks, medications and appointments) across multiple pets, then sorts, filters, flags conflicts and automatically rolls recurring tasks forward.

## Getting started

```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt

python main.py          # CLI demo
streamlit run app.py    # web app
python -m pytest        # tests
```

## 🏗️ Implementation summary

All logic lives in `pawpal_system.py`; `main.py` is a CLI demo and `app.py` is the Streamlit UI.

| Class | Responsibility |
|-------|----------------|
| `Task` (dataclass) | One activity: description, `HH:MM` time, frequency (once/daily/weekly), due date, priority, duration and completion status. `mark_complete()` returns the next occurrence for recurring tasks. |
| `Pet` (dataclass) | A pet's details plus its list of tasks. `add_task()` tags each task with the pet's name. |
| `Owner` | Manages multiple pets. `get_all_tasks()` returns every pet's tasks in one list. |
| `Scheduler` | The "brain". It reads from `Owner.get_all_tasks()` (never from a single pet) so it works across every pet, then sorts, filters, detects conflicts and handles recurrence. |

**How they work together:** an `Owner` has many `Pet`s, each `Pet` has many `Task`s, and the `Scheduler` holds a reference to the `Owner` and asks it for all tasks whenever it builds a schedule.

UML diagrams: [`diagrams/uml_draft.mmd`](diagrams/uml_draft.mmd) (Phase 1) and [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd) (final, also in `diagrams/uml.mmd`).

## ✨ Features

- **Multi-pet management:** one owner, any number of pets, duplicate pet names rejected.
- **Sorting by time:** tasks are listed chronologically, even when added out of order.
- **Priority view:** optional high → medium → low ordering, with time as a tiebreaker.
- **Filtering:** by pet name, by completion status, or both.
- **Daily and weekly recurrence:** completing a recurring task automatically creates the next one.
- **Conflict warnings:** tasks at the same date and time are flagged with a friendly warning instead of an error.
- **Next available slot:** finds the earliest free block of a given length today, using task durations across all pets.
- **Saves your data:** pets and tasks are stored in `data.json`, so they're still there after restarting the app.
- **Input validation:** impossible times like `25:00` are rejected; `9:00` is normalized to `09:00`.

## 📐 Smarter Scheduling

| Feature | Method(s) | How it works |
|---------|-----------|--------------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | `sorted()` with a lambda key of `(due_date, time)`. Times are zero-padded `HH:MM` strings, so string order equals clock order. Priority sort uses `(priority_rank, due_date, time)`. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Starts from `Owner.get_all_tasks()` and applies each filter that is given (pet name is case-insensitive), then sorts by time. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups unfinished tasks by `(due_date, time)` in a dictionary; any slot with 2+ tasks produces a warning string. Never raises, so the app keeps running. |
| Next available slot | `Scheduler.find_next_available_slot()` | Turns each unfinished task into a busy block (`time` to `time + duration_minutes`), sorts the blocks, then walks forward from 07:00 and returns the first gap long enough for the requested duration (or `None` if nothing fits before 21:00). |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Daily tasks get a copy due `today + timedelta(days=1)`, weekly tasks `+ timedelta(weeks=1)`. The scheduler adds the new task to the right pet. One-time tasks don't recur. |

## 🖥️ Sample Output

Output of `python main.py`:

```
🐾 PawPal+ — Today's Schedule for Jordan

📅 Today's Schedule (sorted by time)
------------------------------------------------------------
  ⬜ Fri 10/23 07:00  Morning walk       [Mochi] (daily, high)
  ⬜ Fri 10/23 07:30  Breakfast          [Mochi] (daily, high)
  ⬜ Fri 10/23 07:30  Feed Luna          [Luna] (daily, high)
  ⬜ Fri 10/23 09:00  Flea medication    [Luna] (weekly, medium)
  ⬜ Fri 10/23 14:00  Vet appointment    [Mochi] (once, low)
  ⬜ Fri 10/23 18:30  Evening walk       [Mochi] (daily, high)

🔎 Conflict check
------------------------------------------------------------
  ⚠️ Conflict on 2026-10-23 at 07:30: Breakfast (Mochi), Feed Luna (Luna)

🐶 Mochi's tasks only
------------------------------------------------------------
  ⬜ Fri 10/23 07:00  Morning walk       [Mochi] (daily, high)
  ⬜ Fri 10/23 07:30  Breakfast          [Mochi] (daily, high)
  ⬜ Fri 10/23 14:00  Vet appointment    [Mochi] (once, low)
  ⬜ Fri 10/23 18:30  Evening walk       [Mochi] (daily, high)

✅ Marked 'Breakfast' complete. Next occurrence created for 2026-10-24.

⬜ Still to do
------------------------------------------------------------
  ⬜ Fri 10/23 07:00  Morning walk       [Mochi] (daily, high)
  ⬜ Fri 10/23 07:30  Feed Luna          [Luna] (daily, high)
  ⬜ Fri 10/23 09:00  Flea medication    [Luna] (weekly, medium)
  ⬜ Fri 10/23 14:00  Vet appointment    [Mochi] (once, low)
  ⬜ Fri 10/23 18:30  Evening walk       [Mochi] (daily, high)
  ⬜ Sat 10/24 07:30  Breakfast          [Mochi] (daily, high)

✅ Completed
------------------------------------------------------------
  ✅ Fri 10/23 07:30  Breakfast          [Mochi] (daily, high)

🕒 Next available slot
------------------------------------------------------------
  Earliest free 30-minute block today: 07:45
  Earliest free 90-minute block today: 09:10

⭐ Today by priority (high first)
------------------------------------------------------------
  ⬜ Fri 10/23 07:00  Morning walk       [Mochi] (daily, high)
  ✅ Fri 10/23 07:30  Breakfast          [Mochi] (daily, high)
  ⬜ Fri 10/23 07:30  Feed Luna          [Luna] (daily, high)
  ⬜ Fri 10/23 18:30  Evening walk       [Mochi] (daily, high)
  ⬜ Fri 10/23 09:00  Flea medication    [Luna] (weekly, medium)
  ⬜ Fri 10/23 14:00  Vet appointment    [Mochi] (once, low)
```

## 🧪 Testing PawPal+

Run the tests with:

```bash
python -m pytest
```

The suite (`tests/test_pawpal.py`, 24 tests) covers:

- **Basics:** `mark_complete()` changes status; adding a task increases a pet's task count.
- **Multi-pet:** `Owner.get_all_tasks()` combines pets; duplicate pet names are rejected.
- **Sorting:** chronological order, single-digit hours (`9:00` vs `10:00`), priority-then-time order, and an empty schedule for a pet with no tasks.
- **Filtering:** by pet name and by completion status.
- **Recurrence:** daily → next day, weekly → +7 days, one-time tasks don't recur.
- **Conflicts:** same time across pets is flagged; different times and completed tasks are not.
- **Validation:** invalid times like `25:00` and `12:60` raise `ValueError`.
- **Next available slot:** empty day, busy tasks across pets, gaps too small, completed tasks not blocking, and a full day.
- **Persistence:** save/load round trip keeps every field, and a missing file returns `None`.

Sample test output:

```
============================= test session starts ==============================
platform linux -- Python 3.13.17, pytest-9.1.1, pluggy-1.7.0
cachedir: .pytest_cache
rootdir: C:\Users\saith\Downloads\ai110-module2show-pawpal-starter
plugins: platformdirs-4.12.4, anyio-4.15.1
collecting ... collected 24 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  4%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  8%]
tests/test_pawpal.py::test_owner_get_all_tasks_combines_pets PASSED      [ 12%]
tests/test_pawpal.py::test_duplicate_pet_name_rejected PASSED            [ 16%]
tests/test_pawpal.py::test_sort_by_time_is_chronological PASSED          [ 20%]
tests/test_pawpal.py::test_single_digit_hour_sorts_correctly PASSED      [ 25%]
tests/test_pawpal.py::test_sort_by_priority_then_time PASSED             [ 29%]
tests/test_pawpal.py::test_pet_with_no_tasks_gives_empty_schedule PASSED [ 33%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED               [ 37%]
tests/test_pawpal.py::test_daily_task_creates_next_day_task PASSED       [ 41%]
tests/test_pawpal.py::test_weekly_task_creates_task_one_week_later PASSED [ 45%]
tests/test_pawpal.py::test_one_time_task_does_not_recur PASSED           [ 50%]
tests/test_pawpal.py::test_conflict_detected_for_same_time_across_pets PASSED [ 54%]
tests/test_pawpal.py::test_no_conflict_for_different_times PASSED        [ 58%]
tests/test_pawpal.py::test_completed_tasks_do_not_conflict PASSED        [ 62%]
tests/test_pawpal.py::test_invalid_time_rejected[25:00] PASSED           [ 66%]
tests/test_pawpal.py::test_invalid_time_rejected[12:60] PASSED           [ 70%]
tests/test_pawpal.py::test_next_slot_is_day_start_when_schedule_is_empty PASSED [ 75%]
tests/test_pawpal.py::test_next_slot_skips_busy_tasks_across_pets PASSED [ 79%]
tests/test_pawpal.py::test_next_slot_uses_a_gap_that_is_big_enough PASSED [ 83%]
tests/test_pawpal.py::test_completed_tasks_do_not_block_slots PASSED     [ 87%]
tests/test_pawpal.py::test_no_slot_when_day_is_full PASSED               [ 91%]
tests/test_pawpal.py::test_save_and_load_round_trip PASSED               [ 95%]
tests/test_pawpal.py::test_load_missing_file_returns_none PASSED         [100%]

============================== 24 passed in 0.04s ==============================
```

**Confidence level:** ⭐⭐⭐⭐ (4/5). All happy paths and main edge cases pass. It loses a star because conflict detection only checks exact start times, not overlapping durations.

## 📸 Demo Walkthrough

**Main UI features (`streamlit run app.py`):**

- Set the owner's name.
- Add pets (name, species, age).
- Schedule tasks for a chosen pet with a time, date, repeat setting (once/daily/weekly), priority and duration.
- View today's schedule as a table, sorted by time or by priority.
- See conflict warnings (`st.warning`) above the schedule when two tasks share a time, or a green "no conflicts" message (`st.success`) otherwise.
- Mark a task complete; recurring tasks automatically reappear on their next date.
- Find the earliest free time slot today for a task of any length.
- Browse all tasks with filters by pet and status.
- Everything is saved automatically to `data.json` and reloaded when the app restarts.

**Example workflow:**

1. Enter your name, then add a pet "Mochi" (dog) and a pet "Luna" (cat).
2. Schedule "Morning walk" for Mochi at 08:00, repeating daily, high priority.
3. Schedule "Feed Luna" for Luna at 08:00 as well.
4. The Today's Schedule section lists both tasks in time order and shows a yellow warning that they conflict at 08:00.
5. Mark "Morning walk" complete. A toast confirms the next walk was scheduled for tomorrow, and the warning disappears because only unfinished tasks can conflict.
6. In Browse all tasks, filter to "Mochi" + "To do" to see tomorrow's walk.

**Key Scheduler behaviors shown:** sorting by time and priority, conflict warnings, daily/weekly recurrence and filtering. The CLI demo above shows the same behaviors in the terminal.

## 🚀 Stretch Features

### 1. Advanced algorithm: next available slot (Agent Mode)

`Scheduler.find_next_available_slot(duration_minutes, day, day_start="07:00", day_end="21:00")` goes beyond exact-time conflict checks by using each task's **duration**. It gathers every unfinished task due that day across all pets, treats each one as a busy block, and returns the earliest `"HH:MM"` start time with enough free time. It's shown in `main.py` (see "🕒 Next available slot" in the sample output) and in the app's **Find a free slot** section. The agent workflow is documented in [`ai_interactions.md`](ai_interactions.md).

### 2. Data persistence (JSON)

Pets and tasks are saved to `data.json` so they survive app restarts.

- **Files modified:** `pawpal_system.py` (new `Owner.to_dict()`, `Owner.from_dict()`, `Owner.save_to_json()` and `Owner.load_from_json()`), `app.py` (loads on startup, saves after changes), `.gitignore` (keeps personal `data.json` out of Git) and `tests/test_pawpal.py`.
- **Workflow:**
  1. When the app starts, `Owner.load_from_json("data.json")` rebuilds the owner, pets and tasks. If the file doesn't exist yet, it starts with a new, empty owner.
  2. Every change (renaming the owner, adding a pet, adding a task, marking a task complete) calls `save()`, which runs `owner.save_to_json("data.json")`.
  3. Dates are stored as ISO strings (`"2026-10-23"`) and converted back to `date` objects when loading. `Pet.add_task()` restores each task's `pet_name`.
- To start fresh, delete `data.json`.

### 3. Advanced scheduling: priority-based sorting

Each `Task` has a `priority` of `"high"`, `"medium"` or `"low"`. `Scheduler.sort_by_priority()` sorts by priority first, then by date and time, using a ranking dictionary (`PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}`) in the sort key. In the app, a **Sort by: Time / Priority** toggle switches views.

CLI output from `main.py`, where the same day is shown by time, then by priority:

```
📅 Today's Schedule (sorted by time)
------------------------------------------------------------
  ⬜ Fri 10/23 07:00  Morning walk       [Mochi] (daily, high)
  ⬜ Fri 10/23 07:30  Breakfast          [Mochi] (daily, high)
  ⬜ Fri 10/23 07:30  Feed Luna          [Luna] (daily, high)
  ⬜ Fri 10/23 09:00  Flea medication    [Luna] (weekly, medium)
  ⬜ Fri 10/23 14:00  Vet appointment    [Mochi] (once, low)
  ⬜ Fri 10/23 18:30  Evening walk       [Mochi] (daily, high)

⭐ Today by priority (high first)
------------------------------------------------------------
  ⬜ Fri 10/23 07:00  Morning walk       [Mochi] (daily, high)
  ✅ Fri 10/23 07:30  Breakfast          [Mochi] (daily, high)
  ⬜ Fri 10/23 07:30  Feed Luna          [Luna] (daily, high)
  ⬜ Fri 10/23 18:30  Evening walk       [Mochi] (daily, high)
  ⬜ Fri 10/23 09:00  Flea medication    [Luna] (weekly, medium)
  ⬜ Fri 10/23 14:00  Vet appointment    [Mochi] (once, low)
```

### 4. Professional output formatting

- **Emoji status indicators** in the CLI: `Task.__str__()` prints ✅ for done and ⬜ for to-do tasks, and `main.py` uses emoji section headers (📅 schedule, 🔎 conflicts, 🐶 per-pet view, 🕒 free slot, ⭐ priority).
- **Aligned columns:** `Task.__str__()` uses f-string padding (`{self.description:<18}`) so task names line up in the terminal, and `print_tasks()` in `main.py` adds dividers and handles empty lists.
- **Streamlit components:** `st.table` and `st.dataframe` show tasks as tables (built by `task_rows()` in `app.py`), `st.warning` shows conflicts, `st.success` confirms actions, and `st.toast` announces the next occurrence of a recurring task.
