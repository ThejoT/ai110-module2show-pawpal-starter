# PawPal+ Initiative: Learnings

## 1. System Design

**a. Original Design**

We started by defining three simple operations that the pet owner would have to do: add a pet with its name, species and age; schedule a daily care task, like a walk at 08:00; and order the day's tasks by the order in which they will be performed. I then created a UML diagram with four classes based on these actions. A `Task` is a specific activity with a description, time, frequency, due date and completion status. The `Pet` class contains the pet's information and tasks. The `Owner` can view all the tasks in one place by calling the `get_all_tasks()` method, which matters because an owner can have many pets. The `Scheduler` is the brain of the system. It is responsible for building and organizing the schedule, and it keeps a reference to the `Owner`. Since both the `Task` and `Pet` classes are mostly data, I used Python dataclasses to keep the code concise and readable.

**b. Design Modifications**

My design changed while I was implementing it. When I asked the AI to evaluate my skeleton, it said that it couldn't tell which task belonged to which pet once all the tasks from every pet were put into one list. To remedy this, I added a `pet_name` field to `Task`, which is automatically filled in by `Pet.add_task()`. I also added `priority` and `duration_minutes` to `Task`, since the starter app was already collecting those values. Finally, I added the `task_count()` and `remove_task()` methods to `Pet` so that the UI and tests can interact with a pet's tasks.

---

## 2. Scheduling Logic and Trade-offs

**a. Priorities and Limitations**

My scheduler takes into account four variables: the status of the task, the due date, the time of day and the priority (high, medium or low). I realized that the most important thing in pet care is the clock, because meals and medications happen at set times, so the schedule automatically appears in chronological order. On hectic days, owners can also switch to a priority view to see which tasks cannot be skipped.

**b. Trade-offs**

The main trade-off in my scheduler is that conflict detection only looks at tasks that share the same start time and date. It does not detect overlapping durations, so a 60-minute walk at 8:00 AM and a feeding at 8:30 AM will not be flagged. I think this is a good approach. Most pet care tasks are short, and exact-match checking is easy to read and easy to test. The scheduler also warns the user instead of stopping them, so a missed overlap is low-risk. Another compromise is that `sort_by_time()` sorts the `"HH:MM"` strings using `sorted()` and a lambda key rather than converting them to `datetime` objects. This only works when the times are padded with a zero, so I adjust the time when creating a task (e.g., `9:00` → `09:00`).

---

## 3. AI Collaboration on the Project

**a. Use of AI**

I used an AI coding assistant named Claude throughout the project. It helped me brainstorm the four classes, generate the Mermaid UML diagram, scaffold the class skeleton, code the sorting, filtering, recurrence and conflict detection logic, write the test suite and integrate all of it into the Streamlit UI. It also helped me with some setup issues, like getting my virtual environment working in Git Bash and getting my files into the repo. The best prompts were the ones written around my own files and needs, such as asking how the `Scheduler` should get all tasks from the `Owner`'s pets, or asking for the most important edge cases to test for a scheduler with sorting and recurring tasks.

**b. Assessment and Validation**

The one suggestion I did not implement as-is was to convert each `"HH:MM"` string into a `datetime` object within the sort key. I kept the string-based sorting approach because it is easier to understand, but I added validation that zero-pads every time. I tested this with `test_single_digit_hour_sorts_correctly`, which would fail if 9:00 came after 10:00. I also chose to have conflict detection return warning messages instead of throwing exceptions, so the application doesn't crash when two tasks conflict. After every change the AI made, I ran `python main.py` to check the output and `python -m pytest` to make sure the tests still passed.

**c. Strategy for Artificial Intelligence**

The best feature of the assistant was its ability to edit several files at the same time, which was very important for recurring tasks because that logic affected both `Task` and `Scheduler`. The assistant could also run the demo and tests to prove the code worked. In retrospect, it would have been better to have separate chat threads for design, algorithms and testing, because I was usually in one very long conversation, and a long conversation can mix old code from previous steps with new requests. The most important thing I learned as the "lead architect" is that artificial intelligence can code fast, but I still had to make the architecture decisions. For instance, I had the `Scheduler` work through `Owner.get_all_tasks()` instead of a single pet, kept the design simple and tested all the outcomes.

---

## 4. Testing and Verification

**a. What I Tested**

My test suite has 17 tests. They cover marking tasks as complete, adding tasks to pets, combining tasks across multiple pets, sorting tasks by time and priority, filtering tasks by pet and by completion status, creating daily, weekly and one-time recurrences, checking for conflicts (including checking that completed tasks don't conflict) and rejecting invalid times (like 25:00). These tests are important because conflict detection, recurrence and sorting are the "smart" parts of the application. If any of these components were faulty, the pet owner would get an inaccurate schedule that they might not even notice.

**b. Confidence**

I give myself four stars for confidence. The Streamlit app and the CLI demo both work as expected, and all 17 tests pass. I held back one star because conflict detection only looks for exact start times. If I had more time, I would also test recurring tasks that are completed days after their due date, overlapping tasks, tasks that go past midnight and removing a pet that still has tasks assigned to it.

---

## 5. Reflection

**a. What Went Well**

The best part for me is the separation of the logic layer and the user interface. Because I had already checked everything with `main.py` and pytest, connecting it to Streamlit was just a matter of calling methods I knew worked.

**b. Improvements**

I would add editing and deleting tasks in the UI, and I would save pets and tasks in a JSON file so the data persists across restarts. In a future version, I would also use task durations in conflict detection.

**c. Key Takeaway**

The biggest thing I learned is to put the user interface first. We have a working backend, but the Streamlit application is the actual interface that a pet owner interacts with. Features like sorting and conflict detection only make sense if you can see them on screen, as a sorted table or a visible warning. In future projects, I will plan the user interface early, together with the backend design, instead of leaving it as the last step.
