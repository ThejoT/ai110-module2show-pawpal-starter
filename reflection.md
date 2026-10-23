# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started by identifying three core actions a pet owner needs: adding a pet with its name, species and age; scheduling a care task such as a daily walk at 08:00; and viewing today's tasks in order so they can be marked done. From those actions I designed a UML diagram with four classes. `Task` represents a single activity and holds its description, time, frequency, due date and completion status. `Pet` stores a pet's details along with its own list of tasks. `Owner` manages multiple pets and exposes a `get_all_tasks()` method so the rest of the system can see every task at once. `Scheduler` acts as the "brain": it holds a reference to the `Owner` and is responsible for building and organizing the schedule. I used Python dataclasses for `Task` and `Pet` because they are mostly data, which kept the code short and readable.

**b. Design changes**

My design did change during implementation. When I asked AI to review my skeleton, it pointed out that once tasks from every pet are combined into one list, there is no way to tell which pet a task belongs to. To fix this, I added a `pet_name` field to `Task` that `Pet.add_task()` fills in automatically. I also added `priority` and `duration_minutes` to `Task` because the starter app already collected those values, and I gave `Pet` a `task_count()` and `remove_task()` method so tests and the UI could work with a pet's tasks more easily.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers four constraints: the due date, the time of day, the priority level (high, medium or low) and whether the task is already complete. I decided time mattered most because pet care is driven by the clock. Meals and medications happen at set times, so the default view of the schedule is chronological. Priority is offered as a second view for busy days, when an owner needs to decide which tasks can't be skipped.

**b. Tradeoffs**

The main tradeoff my scheduler makes is that conflict detection only checks for tasks with the exact same date and start time. It does not check overlapping durations, so a 60-minute walk at 08:00 and a feeding at 08:30 won't be flagged. I think this is reasonable because most pet care tasks are short, exact-match checking is simple to read and test, and the scheduler returns a warning instead of blocking the user, so a missed overlap is low-risk. A second tradeoff is that `sort_by_time()` sorts the `"HH:MM"` strings directly with `sorted()` and a lambda key instead of converting them to `datetime` objects. This only works if times are zero-padded, so I normalize every time when a task is created (for example, `9:00` becomes `09:00`).

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude throughout the project as my AI coding assistant. It helped me brainstorm the four classes, generate the Mermaid UML diagram, scaffold the class skeleton, implement the sorting, filtering, recurrence and conflict detection logic, draft the test suite and wire everything into the Streamlit UI. It also helped me with setup problems, like activating my virtual environment in Git Bash and getting my files into the repo. The most helpful prompts were specific ones that referenced my actual files and requirements, such as asking how the `Scheduler` should retrieve all tasks from the `Owner`'s pets, or asking for the most important edge cases to test for a scheduler with sorting and recurring tasks.

**b. Judgment and verification**

One suggestion I did not accept as-is was converting each `"HH:MM"` string into a `datetime` object inside the sort key. I kept the simpler string-based sort because it is easier to read, and instead added validation that zero-pads times. I verified this decision with a test, `test_single_digit_hour_sorts_correctly`, which would fail if `9:00` were sorted after `10:00`. I also chose to have conflict detection return warning messages instead of raising exceptions, so the app never crashes when two tasks overlap. More generally, I verified every AI change by running `python main.py` to check the output by eye and `python -m pytest` to confirm all tests still passed.

**c. AI strategy**

The most effective features were the assistant's ability to edit several files in one change, which mattered for recurring tasks because that logic touched both `Task` and `Scheduler`, and its ability to run the demo and tests to confirm the code actually worked. I worked mostly in one long conversation, and looking back, splitting design, algorithms and testing into separate chat sessions would have kept each conversation more focused, because a long chat mixes old code from earlier phases with new requests. The biggest lesson about being the "lead architect" is that AI can write code very quickly, but I still had to make the structural decisions, such as requiring the `Scheduler` to go through `Owner.get_all_tasks()` instead of a single pet, keep the design simple, and check every result with tests.

---

## 4. Testing and Verification

**a. What you tested**

My test suite has 17 tests. They cover marking a task complete, adding tasks to a pet, combining tasks across multiple pets, sorting chronologically and by priority, filtering by pet and by completion status, daily, weekly and one-time recurrence, conflict detection (including confirming that completed tasks don't cause conflicts) and rejecting invalid times like `25:00`. These tests were important because sorting, recurrence and conflict detection are the "smart" parts of the app, and a bug in any of them would give a pet owner a wrong schedule without any obvious error.

**b. Confidence**

I would rate my confidence at 4 out of 5 stars. All 17 tests pass, and the CLI demo and Streamlit app both behave as expected. I held back one star because the conflict detection only checks exact start times. If I had more time, I would test overlapping durations, tasks that cross midnight, recurring tasks that are completed several days late and removing a pet that still has tasks.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the separation between the logic layer and the UI. Because I verified everything in `main.py` and with pytest first, connecting Streamlit was mostly a matter of calling methods that I already knew worked.

**b. What you would improve**

In another iteration, I would make conflict detection aware of task durations, save pets and tasks to a JSON file so the data survives restarts, and add the ability to edit and delete tasks directly in the UI.

**c. Key takeaway**

The most important thing I learned is to prioritize the UI. A working backend isn't enough on its own, because the Streamlit app is what a pet owner actually sees and uses. Features like sorting and conflict detection only matter if they show up clearly on screen, for example as a sorted table and a visible warning. In future projects, I will plan the user interface earlier, alongside the backend design, instead of treating it as the last step.
