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
- **Input validation:** impossible times like `25:00` are rejected; `9:00` is normalized to `09:00`.

## 📐 Smarter Scheduling

| Feature | Method(s) | How it works |
|---------|-----------|--------------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | `sorted()` with a lambda key of `(due_date, time)`. Times are zero-padded `HH:MM` strings, so string order equals clock order. Priority sort uses `(priority_rank, due_date, time)`. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Starts from `Owner.get_all_tasks()` and applies each filter that is given (pet name is case-insensitive), then sorts by time. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups unfinished tasks by `(due_date, time)` in a dictionary; any slot with 2+ tasks produces a warning string. Never raises, so the app keeps running. |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Daily tasks get a copy due `today + timedelta(days=1)`, weekly tasks `+ timedelta(weeks=1)`. The scheduler adds the new task to the right pet. One-time tasks don't recur. |

## 🖥️ Sample Output

Output of `python main.py`:

```
🐾 PawPal+ — Today's Schedule for Jordan

📅 Today's Schedule (sorted by time)
------------------------------------------------------------
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
  ⬜ Fri 10/23 07:30  Breakfast          [Mochi] (daily, high)
  ⬜ Fri 10/23 14:00  Vet appointment    [Mochi] (once, low)
  ⬜ Fri 10/23 18:30  Evening walk       [Mochi] (daily, high)

✅ Marked 'Breakfast' complete. Next occurrence created for 2026-10-24.

⬜ Still to do
------------------------------------------------------------
  ⬜ Fri 10/23 07:30  Feed Luna          [Luna] (daily, high)
  ⬜ Fri 10/23 09:00  Flea medication    [Luna] (weekly, medium)
  ⬜ Fri 10/23 14:00  Vet appointment    [Mochi] (once, low)
  ⬜ Fri 10/23 18:30  Evening walk       [Mochi] (daily, high)
  ⬜ Sat 10/24 07:30  Breakfast          [Mochi] (daily, high)

✅ Completed
------------------------------------------------------------
  ✅ Fri 10/23 07:30  Breakfast          [Mochi] (daily, high)

⭐ Today by priority (high first)
------------------------------------------------------------
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

The suite (`tests/test_pawpal.py`, 17 tests) covers:

- **Basics:** `mark_complete()` changes status; adding a task increases a pet's task count.
- **Multi-pet:** `Owner.get_all_tasks()` combines pets; duplicate pet names are rejected.
- **Sorting:** chronological order, single-digit hours (`9:00` vs `10:00`), priority-then-time order, and an empty schedule for a pet with no tasks.
- **Filtering:** by pet name and by completion status.
- **Recurrence:** daily → next day, weekly → +7 days, one-time tasks don't recur.
- **Conflicts:** same time across pets is flagged; different times and completed tasks are not.
- **Validation:** invalid times like `25:00` and `12:60` raise `ValueError`.

Sample test output:

```
============================= test session starts ==============================
platform linux -- Python 3.13.17, pytest-9.1.1, pluggy-1.7.0
cachedir: .pytest_cache
rootdir: C:\Users\saith\Downloads\ai110-module2show-pawpal-starter
plugins: platformdirs-4.12.4, anyio-4.15.1
collecting ... collected 17 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  5%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 11%]
tests/test_pawpal.py::test_owner_get_all_tasks_combines_pets PASSED      [ 17%]
tests/test_pawpal.py::test_duplicate_pet_name_rejected PASSED            [ 23%]
tests/test_pawpal.py::test_sort_by_time_is_chronological PASSED          [ 29%]
tests/test_pawpal.py::test_single_digit_hour_sorts_correctly PASSED      [ 35%]
tests/test_pawpal.py::test_sort_by_priority_then_time PASSED             [ 41%]
tests/test_pawpal.py::test_pet_with_no_tasks_gives_empty_schedule PASSED [ 47%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED               [ 52%]
tests/test_pawpal.py::test_daily_task_creates_next_day_task PASSED       [ 58%]
tests/test_pawpal.py::test_weekly_task_creates_task_one_week_later PASSED [ 64%]
tests/test_pawpal.py::test_one_time_task_does_not_recur PASSED           [ 70%]
tests/test_pawpal.py::test_conflict_detected_for_same_time_across_pets PASSED [ 76%]
tests/test_pawpal.py::test_no_conflict_for_different_times PASSED        [ 82%]
tests/test_pawpal.py::test_completed_tasks_do_not_conflict PASSED        [ 88%]
tests/test_pawpal.py::test_invalid_time_rejected[25:00] PASSED           [ 94%]
tests/test_pawpal.py::test_invalid_time_rejected[12:60] PASSED           [100%]

============================== 17 passed in 0.06s ==============================
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
- Browse all tasks with filters by pet and status.

**Example workflow:**

1. Enter your name, then add a pet "Mochi" (dog) and a pet "Luna" (cat).
2. Schedule "Morning walk" for Mochi at 08:00, repeating daily, high priority.
3. Schedule "Feed Luna" for Luna at 08:00 as well.
4. The Today's Schedule section lists both tasks in time order and shows a yellow warning that they conflict at 08:00.
5. Mark "Morning walk" complete. A toast confirms the next walk was scheduled for tomorrow, and the warning disappears because only unfinished tasks can conflict.
6. In Browse all tasks, filter to "Mochi" + "To do" to see tomorrow's walk.

**Key Scheduler behaviors shown:** sorting by time and priority, conflict warnings, daily/weekly recurrence and filtering. The CLI demo above shows the same behaviors in the terminal.
