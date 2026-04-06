"""
main.py — Demo script for PawPal+ logic layer.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Set up owner ---
    owner = Owner("Jordan")

    # --- Create pets ---
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Morning walk",    "07:00", 30, "daily"))
    mochi.add_task(Task("Breakfast",       "07:30", 10, "daily"))
    mochi.add_task(Task("Evening walk",    "18:00", 30, "daily"))

    luna = Pet("Luna", "cat")
    luna.add_task(Task("Morning feeding",  "08:00",  5, "daily"))
    luna.add_task(Task("Playtime",         "17:00", 15, "daily"))
    luna.add_task(Task("Evening feeding",  "18:30",  5, "daily"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- Create scheduler and print full schedule ---
    scheduler = Scheduler(owner)
    print("=== FULL SCHEDULE ===")
    scheduler.print_schedule()

    # --- Simulate completing some morning tasks ---
    scheduler.mark_task_complete("Mochi", "Morning walk")
    scheduler.mark_task_complete("Mochi", "Breakfast")
    scheduler.mark_task_complete("Luna",  "Morning feeding")

    # --- Show updated schedule ---
    print("=== AFTER COMPLETING MORNING TASKS ===")
    scheduler.print_schedule()

    # --- Show only pending tasks ---
    pending = scheduler.get_pending_tasks()
    print("Remaining tasks for today:")
    for pet_name, task in pending:
        print(f"  • {pet_name}: {task.description} at {task.time} ({task.duration} min)")


if __name__ == "__main__":
    main()
