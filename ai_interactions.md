# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Stretch feature: **Advanced Algorithmic Capability via Agent Mode**. The third algorithm is `Scheduler.find_next_available_slot()`.

**What task did you give the agent?**

I gave Claude the PawPal+ grading rubric and asked it to follow it for my project. For this stretch feature, that meant adding a third algorithmic capability beyond sorting, filtering, recurrence and conflict detection. Claude chose a "next available slot" finder, because my conflict detection only compares exact start times and ignores the `duration_minutes` field each task already had. The slot finder is the first feature that actually uses durations.

**What did the agent do?**

Claude worked directly in my GitHub repo and made these changes:

| File | Change |
|------|--------|
| `pawpal_system.py` | Added `Scheduler.find_next_available_slot()` plus two helpers, `_to_minutes()` and `_to_hhmm()`, to convert between `"HH:MM"` and minutes after midnight. |
| `tests/test_pawpal.py` | Added 5 tests: an empty day, busy tasks across two pets, a gap that is too small, completed tasks not blocking time, and a completely full day. |
| `main.py` | Gave the demo tasks realistic durations, added a "Morning walk" at 07:00, and printed the earliest free 30- and 90-minute blocks. |
| `app.py` | Added a **Find a free slot** section with a minutes input and a button that shows the result with `st.success` / `st.warning`. |
| `diagrams/uml_final.mmd`, `diagrams/uml.mmd` | Added the new method to the `Scheduler` class. |
| `README.md` | Added the method to the Smarter Scheduling table and a Stretch Features section, and refreshed the sample output and test output. |

How the algorithm works: it turns each unfinished task due that day (across all pets) into a busy block from its start time to start + duration, sorts the blocks, then walks forward from 07:00. If the requested duration fits before the next busy block starts, that's the answer. Otherwise it jumps to the end of that block. If nothing fits before 21:00, it returns `None`.

Claude then ran `python -m pytest` (24 passed), ran `python main.py`, and tested the Streamlit app with a script that clicked **Find slot**. It checked the demo output by hand: with tasks at 07:00–07:30, 07:30–07:45 and 09:00–09:10, the earliest 30-minute block is 07:45, and the earliest 90-minute block is 09:10, because 07:45 + 90 minutes would run into the 09:00 medication.

**What did you have to verify or fix manually?**

I had to verify task accuracy. I checked that the tasks in the demo and the app showed the correct pet, time, duration, priority and repeat setting, and that the free slots the agent's code returned actually matched those tasks. For example, the 30-minute slot came out at 07:45, right after Breakfast and Feed Luna end, and the 90-minute slot skipped past the 09:00 flea medication. I didn't need to make any code changes after checking.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
