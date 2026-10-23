"""PawPal+ Streamlit UI, wired to the logic layer in pawpal_system.py."""

from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care planner: track feedings, walks, meds and appointments.")

# --------------------------------------------------------------------------- #
# Session "memory": create the Owner once and keep it across reruns
# --------------------------------------------------------------------------- #
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def task_rows(tasks):
    """Convert Task objects into dicts for st.table / st.dataframe."""
    return [
        {
            "Done": "✅" if t.completed else "⬜",
            "Date": t.due_date.strftime("%a %b %d"),
            "Time": t.time,
            "Pet": t.pet_name,
            "Task": t.description,
            "Repeats": t.frequency,
            "Priority": t.priority,
            "Minutes": t.duration_minutes,
        }
        for t in tasks
    ]


# --------------------------------------------------------------------------- #
# Owner + pets
# --------------------------------------------------------------------------- #
st.subheader("👤 Owner")
new_name = st.text_input("Owner name", value=owner.name)
if new_name and new_name != owner.name:
    owner.name = new_name

st.subheader("🐶 Add a pet")
with st.form("add_pet", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    pet_name = c1.text_input("Pet name")
    species = c2.selectbox("Species", ["dog", "cat", "other"])
    age = c3.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        else:
            try:
                owner.add_pet(Pet(pet_name.strip(), species, int(age)))
                st.success(f"Added {pet_name}!")
            except ValueError as err:
                st.error(str(err))

if owner.pets:
    st.write("**Your pets:** " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above to start scheduling tasks.")

# --------------------------------------------------------------------------- #
# Schedule a task
# --------------------------------------------------------------------------- #
if owner.pets:
    st.subheader("📝 Schedule a task")
    with st.form("add_task", clear_on_submit=True):
        c1, c2 = st.columns(2)
        task_pet = c1.selectbox("For which pet?", [p.name for p in owner.pets])
        description = c2.text_input("Task", value="Morning walk")
        c3, c4, c5 = st.columns(3)
        task_time = c3.time_input("Time", value=time(8, 0), step=900)
        task_date = c4.date_input("Date", value=date.today())
        frequency = c5.selectbox("Repeats", ["once", "daily", "weekly"])
        c6, c7 = st.columns(2)
        priority = c6.selectbox("Priority", ["high", "medium", "low"], index=1)
        duration = c7.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        if st.form_submit_button("Add task"):
            owner.get_pet(task_pet).add_task(Task(
                description=description.strip() or "Task",
                time=task_time.strftime("%H:%M"),
                frequency=frequency,
                due_date=task_date,
                priority=priority,
                duration_minutes=int(duration),
            ))
            st.success(f"Scheduled '{description}' for {task_pet} at {task_time:%H:%M}.")

st.divider()

# --------------------------------------------------------------------------- #
# Today's schedule + conflict warnings
# --------------------------------------------------------------------------- #
st.subheader("📅 Today's schedule")
sort_mode = st.radio("Sort by", ["Time", "Priority"], horizontal=True)
todays = scheduler.get_todays_schedule()
if sort_mode == "Priority":
    todays = scheduler.sort_by_priority(todays)

conflicts = scheduler.detect_conflicts(todays)
if conflicts:
    for warning in conflicts:
        st.warning(warning + " — consider moving one of these tasks.")
elif todays:
    st.success("No scheduling conflicts today. 🎉")

if todays:
    st.table(task_rows(todays))
else:
    st.info("Nothing scheduled for today.")

# --------------------------------------------------------------------------- #
# Mark tasks complete (recurring tasks roll forward automatically)
# --------------------------------------------------------------------------- #
open_today = [t for t in todays if not t.completed]
if open_today:
    st.subheader("✅ Mark a task complete")
    labels = {f"{t.time} · {t.description} ({t.pet_name})": t for t in open_today}
    choice = st.selectbox("Task", list(labels))
    if st.button("Mark complete"):
        nxt = scheduler.mark_task_complete(labels[choice])
        if nxt:
            st.toast(f"Done! Next '{nxt.description}' scheduled for {nxt.due_date:%a %b %d}.")
        else:
            st.toast("Done!")
        st.rerun()

st.divider()

# --------------------------------------------------------------------------- #
# Filter all tasks
# --------------------------------------------------------------------------- #
st.subheader("🔍 Browse all tasks")
c1, c2 = st.columns(2)
pet_filter = c1.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets])
status_filter = c2.selectbox("Status", ["All", "To do", "Completed"])

filtered = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All pets" else pet_filter,
    completed={"All": None, "To do": False, "Completed": True}[status_filter],
)
if filtered:
    st.dataframe(task_rows(filtered), hide_index=True)
else:
    st.info("No tasks match these filters.")
