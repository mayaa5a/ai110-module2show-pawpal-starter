"""
main.py — Demo script for PawPal+ logic layer.
Demonstrates: schedule creation, sorting, filtering, recurring tasks, conflict detection.
Run with: python3 main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def separator(title: str) -> None:
    print(f"\n{'─' * 52}")
    print(f"  {title}")
    print(f"{'─' * 52}")


def main():
    # ── Setup ────────────────────────────────────────────────────────────────
    owner = Owner("Jordan")

    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Morning walk",   "07:00", 30,  "daily"))
    mochi.add_task(Task("Breakfast",      "07:30", 10,  "daily"))
    mochi.add_task(Task("Evening walk",   "18:00", 30,  "daily"))
    # Add out-of-order intentionally to verify sort
    mochi.add_task(Task("Afternoon nap",  "13:00", 20,  "once"))

    luna = Pet("Luna", "cat")
    luna.add_task(Task("Morning feeding", "08:00",  5,  "daily"))
    luna.add_task(Task("Playtime",        "17:00", 15,  "daily"))
    luna.add_task(Task("Evening feeding", "18:15",  5,  "daily"))
    # Intentional conflict: overlaps with Mochi's Evening walk (18:00-18:30)
    luna.add_task(Task("Vet call",        "18:10", 25,  "once"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)

    # ── 1. Sorted full schedule ───────────────────────────────────────────────
    separator("1. FULL SCHEDULE (sorted by time)")
    scheduler.print_schedule()

    # ── 2. Conflict detection ────────────────────────────────────────────────
    separator("2. CONFLICT DETECTION")
    conflicts = scheduler.get_conflicts()
    if conflicts:
        for name_a, task_a, name_b, task_b in conflicts:
            print(
                f"  ⚠️  {name_a}/{task_a.description} ({task_a.time}, {task_a.duration} min)"
                f" overlaps {name_b}/{task_b.description} ({task_b.time}, {task_b.duration} min)"
            )
    else:
        print("  No conflicts.")

    # ── 3. Mark tasks complete + recurrence ──────────────────────────────────
    separator("3. MARK MORNING TASKS DONE (recurring tasks get next occurrence)")
    scheduler.mark_task_complete("Mochi", "Morning walk")   # daily → next occurrence added
    scheduler.mark_task_complete("Mochi", "Breakfast")      # daily
    scheduler.mark_task_complete("Luna",  "Morning feeding") # daily

    scheduler.print_schedule()

    # ── 4. Pending tasks only ────────────────────────────────────────────────
    separator("4. PENDING TASKS (filter: completed=False)")
    for pet_name, task in scheduler.get_pending_tasks():
        print(f"  • {pet_name}: {task.description} at {task.time} ({task.duration} min)")

    # ── 5. Filter by pet ─────────────────────────────────────────────────────
    separator("5. FILTER: Luna's tasks only")
    for pet_name, task in scheduler.filter_tasks(pet_name="Luna"):
        status = "✓" if task.completed else "○"
        print(f"  [{status}] {task.time}  {task.description}")

    # ── 6. Filter by status ──────────────────────────────────────────────────
    separator("6. FILTER: Completed tasks only")
    completed = scheduler.filter_tasks(completed=True)
    if completed:
        for pet_name, task in completed:
            print(f"  ✓ {pet_name}: {task.description}")
    else:
        print("  None yet.")


if __name__ == "__main__":
    main()
