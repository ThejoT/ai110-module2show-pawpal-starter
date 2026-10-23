"""CLI demo for PawPal+: verifies the logic layer before using the Streamlit UI."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, tasks) -> None:
    """Print a heading followed by one task per line."""
    print(f"\n{title}")
    print("-" * 60)
    if not tasks:
        print("  (no tasks)")
    for task in tasks:
        print(f"  {task}")


def main() -> None:
    # --- Set up an owner with two pets ---
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- Add tasks deliberately OUT OF ORDER to prove sorting works ---
    mochi.add_task(Task("Evening walk", "18:30", frequency="daily", priority="high", duration_minutes=45))
    mochi.add_task(Task("Breakfast", "07:30", frequency="daily", priority="high", duration_minutes=15))
    luna.add_task(Task("Flea medication", "09:00", frequency="weekly", priority="medium", duration_minutes=10))
    luna.add_task(Task("Feed Luna", "07:30", frequency="daily", priority="high"))  # same time as Breakfast
    mochi.add_task(Task("Vet appointment", "14:00", priority="low", duration_minutes=60))
    mochi.add_task(Task("Morning walk", "07:00", frequency="daily", priority="high", duration_minutes=30))

    scheduler = Scheduler(owner)

    # --- Today's schedule (sorted by time) ---
    print(f"🐾 PawPal+ — Today's Schedule for {owner.name}")
    print_tasks("📅 Today's Schedule (sorted by time)", scheduler.get_todays_schedule())

    # --- Conflict detection ---
    print("\n🔎 Conflict check")
    print("-" * 60)
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        print(f"  {warning}")
    if not conflicts:
        print("  No conflicts found.")

    # --- Filtering by pet ---
    print_tasks("🐶 Mochi's tasks only", scheduler.filter_tasks(pet_name="Mochi"))

    # --- Recurring task: complete Mochi's daily breakfast ---
    breakfast = next(t for t in mochi.tasks if t.description == "Breakfast")
    next_one = scheduler.mark_task_complete(breakfast)
    print(f"\n✅ Marked '{breakfast.description}' complete. "
          f"Next occurrence created for {next_one.due_date}.")

    # --- Filtering by status ---
    print_tasks("⬜ Still to do", scheduler.filter_tasks(completed=False))
    print_tasks("✅ Completed", scheduler.filter_tasks(completed=True))

    # --- Next available slot (uses task durations across all pets) ---
    print("\n🕒 Next available slot")
    print("-" * 60)
    for minutes in (30, 90):
        slot = scheduler.find_next_available_slot(minutes)
        print(f"  Earliest free {minutes}-minute block today: {slot or 'none'}")

    # --- Priority view ---
    print_tasks("⭐ Today by priority (high first)",
                scheduler.sort_by_priority(scheduler.get_todays_schedule()))


if __name__ == "__main__":
    main()
