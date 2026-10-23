# PawPal+ Project Reflection

> ✏️ This is a draft. Edit it so it describes **your** experience in your own words.

## 1. System Design

**Core user actions**

1. Add a pet (name, species, age) to their account.
2. Schedule a care task for a pet (e.g., a daily walk at 08:00).
3. See today's tasks in order, and mark them done.

**a. Initial design**

My UML had four classes. `Task` holds a single activity (description, time, frequency, due date, completion status). `Pet` holds a pet's details and its list of tasks. `Owner` manages multiple pets and exposes `get_all_tasks()` so the rest of the system can see every task at once. `Scheduler` is the "brain": it holds a reference to the `Owner` and is responsible for building and organizing the schedule. I used dataclasses for `Task` and `Pet` because they are mostly data, which keeps the code short.

**b. Design changes**

Yes. When I asked AI to review the skeleton, it pointed out that once tasks from all pets are combined into one list, there is no way to tell which pet a task belongs to. I added a `pet_name` field to `Task` that `Pet.add_task()` fills in automatically. I also added `priority` and `duration_minutes` to `Task` because the starter app already collected them, and `task_count()`/`remove_task()` to `Pet`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers the due date, time of day, priority (high/medium/low) and completion status. Time mattered most because pet care is driven by the clock (meals and meds at set times), so the default view is chronological. Priority is offered as a second view for days when the owner needs to decide what can't be skipped.

**b. Tradeoffs**

Conflict detection only checks for tasks with the exact same date and start time. It does not check overlapping durations (a 60-minute walk at 08:00 and a feeding at 08:30 won't be flagged). This is reasonable because most pet tasks are short, exact-match checking is simple to read and test, and it returns a warning instead of blocking the user, so a missed overlap is low-risk.

Another tradeoff: I kept `sort_by_time()` as `sorted()` with a lambda on `(due_date, time)` rather than converting strings to `datetime` objects. It relies on times being zero-padded, so I normalize times in `Task.__post_init__` (`9:00` → `09:00`).

---

## 3. AI Collaboration

**a. How you used AI**

I used AI to brainstorm the four classes, generate the Mermaid UML, scaffold the skeleton, implement the algorithms, draft tests, and wire up the Streamlit UI. The most helpful prompts were specific and referenced my files, such as "Based on my skeletons in pawpal_system.py, how should the Scheduler retrieve all tasks from the Owner's pets?" and "What are the most important edge cases to test for a pet scheduler with sorting and recurring tasks?"

**b. Judgment and verification**

AI suggested converting each `HH:MM` string into a `datetime` inside the sort key. I kept the simpler string-based sort because it's easier to read, and instead added validation that zero-pads times. I verified this with a test (`test_single_digit_hour_sorts_correctly`) that would fail if `9:00` were sorted after `10:00`. I also checked every AI change by running `python main.py` and `python -m pytest`.

**AI strategy**

- **Most effective features:** agent/edit mode for changes that touched multiple files (recurrence affected both `Task` and `Scheduler`), and chat for explaining test code before I saved it.
- **Rejected/modified suggestion:** the `datetime` sort key above. I also rejected raising an exception on conflicts and used warning strings instead, so the app never crashes.
- **Separate chat sessions:** keeping design, algorithms and testing in different chats meant each conversation stayed focused and the AI wasn't confused by old code from earlier phases.
- **Being the lead architect:** AI writes code fast, but I had to decide the structure (e.g., the Scheduler must go through `Owner.get_all_tasks()`), keep it simple, and verify everything with tests.

---

## 4. Testing and Verification

**a. What you tested**

17 tests covering task completion, adding tasks, combining tasks across pets, chronological and priority sorting, filtering by pet and status, daily/weekly/one-time recurrence, conflict detection (including that completed tasks don't conflict), and invalid time input. These matter because sorting, recurrence and conflicts are the "smart" parts of the app, and bugs there would give an owner a wrong schedule.

**b. Confidence**

4/5. All tests pass. Next I would test overlapping durations, tasks that cross midnight, recurring tasks completed late (several days after the due date), and removing a pet that still has tasks.

---

## 5. Reflection

**a. What went well**

The separation between the logic layer and the UI. Because everything was verified in `main.py` and pytest first, connecting Streamlit was mostly just calling existing methods.

**b. What you would improve**

Duration-aware conflict detection, saving data to JSON so it survives restarts, and editing/deleting tasks in the UI.

**c. Key takeaway**

Design first, then let AI help with implementation. A clear UML made my prompts better and made it easy to spot when AI output didn't fit the design.
