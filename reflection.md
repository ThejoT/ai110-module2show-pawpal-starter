# PawPal+ Initiative: Learnings

## 1. System Design
**a. original design**

We started by defining three simple operations that the pet owner would have to do: add a pet with its name, species and age; schedule a daily care task like a walk at 08:00; and order the tasks of the day by the order in which they will be performed. So I created a UML diagram with four classes based on these actions. A task is a specific activity with a description, time, frequency, due date and completion status. The pet contains the pet’s information and tasks. The owner can view all the tasks in one place. He does this by calling the get_all_tasks() method. This is because there are so many pets. The Schedule is the brain of the system. It is responsible for scheduling and construction. It keeps a record of the Owner. As both the Task and Pet classes are mostly data, I have used Python dataclasses to keep the code concise and readable.

**b) Design modifications**

My design was altered while being implemented. When I asked it to evaluate my skeleton it said that it couldn't tell which task belonged to which pet when all the tasks from each pet were put into one list. To remedy this, I added a pet_name field to Task, which is automatically populated by Pet.add_task(). I also added priority and duration_minutes to Task, since the starter app was already collecting those values. I also added the task_count() and remove_task() methods to Pet so that the UI and tests can interact with a pet’s tasks.

---

## 2. Scheduling Logic and Trade-offs
**a. Priorities and limitations**

I have a scheduler that takes into account four variables: the status of the task, the due date, the time of day and the priority (high, medium or low). And I realized that the most important thing in pet care is a clock, because the most important thing is time. Meals and medications are scheduled so the schedule automatically appears in chronological order. Owners are presented with a different point of view when faced with the conundrum of setting duties that cannot be disregarded on hectic days.

**b. Discounted.**

The main trade-off in my scheduler is that conflict detection only looks at assignments that share the same start time and date. It does not detect overlapping durations, so a 60 minute walk at 8:00 AM and a feed at 8:30 AM will not be detected. I think this is a good way to go. Most pet care tasks are short term. Exact match testing is easy to read and easy to do. The scheduler warns the user not to halt the user, so it is less likely that an overlap is missed. sort by time () sorts the "HH:MM" strings using sorted () and a lambda key rather than converting to datetime objects. That's another compromise. This is due to the times being padded with 0. So I change time when creating a task (e.g. 9:00 -> 09:00).

---

## 3. AI-Collaborating on Projects
**a. use of AI**

I had an AI coding assistant named Claude to help me throughout the project. I used it for generating the Mermaid UML diagram, scaffolding the class skeleton, coding the sorting, filtering, recurrence and conflict detection logic, writing the test suite and integrating all of the above into the Streamlit UI. It also helped me in the development of the four courses. It helped me with some setup issues as well, like making sure that my virtual environment was working in Git Bash and getting my files into the repo. The best prompts were the ones I made for my own files and my own needs. For example, prompts such as how should the Scheduler get all tasks from the Owner's pets, or the most important edge cases to test for a scheduler with sorting and recurring tasks.

**b. Assessment and validation**

The one suggestion I did not implement as-is was to convert each “HH:MM” string into a datetime object within the sort key. I kept the string-based sorting approach as is more understandable but added validation that no padding is allowed. tested in test “test_single_digit_hour_sorts_correctly”. The exam would be a failure if 9:00 came after 10:00. I also thought about generating warning messages in the conflict detection report instead of throwing exceptions to prevent the application from crashing when two tasks are in conflict. I would usually just run python main.py to see the output, and python -m pytest to make sure the tests still passed after making changes to the AI.

**c. Strategy for Artificial Intelligence**

The best part of the assistant was the possibility to edit several files at the same time, which was very important for the recurring activities, because the logic applied to the Task and the Scheduler. The assistant also had the advantage of being able to do the demonstration and tests to prove the code worked. It would have been better to have separate chat threads for design, algorithms and testing topics. In retrospect, I was often in one very long conversation. That's because in a long conversation you might get old code from previous steps mixed with new requests. The most important thing I've learned as the "architect of everything" is that artificial intelligence can code fast. But I had to make some architecture decisions. For instance, I also had the Scheduler loop over Owner.get_all_tasks() instead of a single pet, kept it simple, and tested all outcomes.

---

## 4. Test and verification.
**A. Discussion topics**

I have a test suite with 17 tests;. Mark tasks as complete Make animals work Jobs among many animals combine Sort tasks by importance and date. Filter tasks by pet and by completion status Create daily, weekly and one-off recurrences Check for conflicts (including check that completed tasks don’t conflict) Reject invalid times (like 25:00) These tests are important as the conflict detection, recurrence, and sorting are the “smart” parts of the application. So if any of these components is faulty the pet owner will get an inaccurate schedule that they may not even notice.

**b. Belief**

So I get four stars from myself in confidence. The Streamlit app and the CLI demo are both working as expected. All seventeen assessments are a success. I give it 4 stars because it does the process of finding conflicts, but it only looks for exact start times. If I had more time, I would also do duplicate tasks that are done days after the due date, overlapping tasks, tasks that go after midnight, and tasks that require removal of a pet that has tasks assigned to it.

---

## 5. Reflecting Thought
**a. The Advantages**

The best part for me is the separation of the logic layer and the user interface. I have already checked everything with main.py and pytest, I just applied the techniques I know to connect to Streamlit.

**b. Improvements?**

I would add editing and deleting tasks in the UI, and would save pets and tasks in a JSON file so the data persists across restarts. In a future version I’d also add task durations in conflict detection.

**c. The key part:**

The biggest thing I learned from that is to put the user interface first. We have a working backend, but the actual interface that a pet owner interacts with is the streamlit application. It makes sense to have things like sorting, conflict detection, etc. if you can see it on screen, a sorted table, a visible warning. In future projects I will try to plan the user interface first and not as the last step together with the backend design.
