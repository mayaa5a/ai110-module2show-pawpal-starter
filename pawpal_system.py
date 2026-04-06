"""
PawPal+ Logic Layer
Core classes for the pet care scheduling system.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' string to total minutes since midnight."""
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


# ─── Task ─────────────────────────────────────────────────────────────────────

@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str               # "HH:MM" 24-hour format
    duration: int           # minutes
    frequency: str          # "daily" | "weekly" | "once"
    completed: bool = False
    due_date: Optional[str] = None  # ISO date string, e.g. "2026-04-05"; None = today

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset this task to incomplete status."""
        self.completed = False

    def __str__(self) -> str:
        """Return a human-readable one-line summary of the task."""
        status = "✓" if self.completed else "○"
        due = f" [{self.due_date}]" if self.due_date else ""
        return (
            f"[{status}] {self.time}{due} - {self.description} "
            f"({self.duration} min, {self.frequency})"
        )


# ─── Pet ──────────────────────────────────────────────────────────────────────

@dataclass
class Pet:
    """Stores pet details and manages its list of tasks."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's schedule."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove a task by description; returns True if a task was removed."""
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.description != description]
        return len(self.tasks) < original_count

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


# ─── Owner ────────────────────────────────────────────────────────────────────

class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str) -> None:
        """Initialize an owner with a name and an empty pet list."""
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection."""
        self.pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def get_all_tasks(self) -> List[tuple]:
        """Return a flat list of (pet, task) tuples across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


# ─── Scheduler ────────────────────────────────────────────────────────────────

class Scheduler:
    """The 'brain' that retrieves, organizes, and manages tasks across pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with an owner whose pets will be scheduled."""
        self.owner = owner

    # ── Core retrieval ────────────────────────────────────────────────────────

    def get_schedule(self) -> List[tuple]:
        """Return today's (pet_name, task) pairs sorted chronologically by time.

        Tasks with no due_date are treated as 'today'. Tasks with a future
        due_date are excluded so next-occurrence copies don't pollute today's view.
        """
        today = date.today().isoformat()
        all_tasks = [
            (pet.name, task)
            for pet in self.owner.get_pets()
            for task in pet.get_tasks()
            if task.due_date is None or task.due_date == today
        ]
        return sorted(all_tasks, key=lambda x: x[1].time)

    def get_tasks_by_time(self, time: str) -> List[tuple]:
        """Return all tasks scheduled at a specific time (HH:MM)."""
        return [pair for pair in self.get_schedule() if pair[1].time == time]

    # ── Filtering ─────────────────────────────────────────────────────────────

    def get_pending_tasks(self) -> List[tuple]:
        """Return only tasks that have not yet been completed."""
        return [(name, task) for name, task in self.get_schedule() if not task.completed]

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[tuple]:
        """Return tasks filtered by pet name and/or completion status.

        Args:
            pet_name:  If given, only include tasks for this pet.
            completed: If True, only completed tasks; if False, only pending; if None, all.
        """
        results = self.get_schedule()
        if pet_name is not None:
            results = [(n, t) for n, t in results if n == pet_name]
        if completed is not None:
            results = [(n, t) for n, t in results if t.completed == completed]
        return results

    # ── Completion & recurrence ───────────────────────────────────────────────

    def mark_task_complete(self, pet_name: str, description: str) -> bool:
        """Mark a task complete and schedule the next occurrence for recurring tasks.

        Returns True if the task was found and marked, False otherwise.
        For 'daily' tasks the next occurrence is created for tomorrow;
        for 'weekly' tasks, seven days from today.
        """
        for pet in self.owner.get_pets():
            if pet.name != pet_name:
                continue
            for task in pet.get_tasks():
                if task.description != description or task.completed:
                    continue
                task.mark_complete()
                # Schedule next occurrence for recurring tasks
                if task.frequency == "daily":
                    next_date = (date.today() + timedelta(days=1)).isoformat()
                elif task.frequency == "weekly":
                    next_date = (date.today() + timedelta(weeks=1)).isoformat()
                else:
                    next_date = None
                if next_date:
                    pet.add_task(Task(
                        description=task.description,
                        time=task.time,
                        duration=task.duration,
                        frequency=task.frequency,
                        due_date=next_date,
                    ))
                return True
        return False

    # ── Conflict detection ────────────────────────────────────────────────────

    def get_conflicts(self) -> List[tuple]:
        """Detect tasks whose time windows overlap (across all pets).

        Returns a list of (pet_a_name, task_a, pet_b_name, task_b) tuples.
        Uses interval overlap: two tasks conflict when one starts before the other ends.
        """
        schedule = self.get_schedule()
        conflicts = []
        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                name_a, task_a = schedule[i]
                name_b, task_b = schedule[j]
                start_a = _time_to_minutes(task_a.time)
                start_b = _time_to_minutes(task_b.time)
                end_a = start_a + task_a.duration
                end_b = start_b + task_b.duration
                if start_a < end_b and start_b < end_a:
                    conflicts.append((name_a, task_a, name_b, task_b))
        return conflicts

    # ── Display ───────────────────────────────────────────────────────────────

    def print_schedule(self) -> None:
        """Print a formatted today's schedule to the terminal."""
        schedule = self.get_schedule()
        conflicts = self.get_conflicts()
        print(f"\n{'=' * 52}")
        print(f"  Today's Schedule for {self.owner.name}")
        print(f"{'=' * 52}")
        if not schedule:
            print("  No tasks scheduled.")
        else:
            for pet_name, task in schedule:
                status = "✓" if task.completed else "○"
                due = f" [{task.due_date}]" if task.due_date else ""
                print(
                    f"  [{status}] {task.time}{due}  |  {pet_name:<12}|  "
                    f"{task.description} ({task.duration} min)"
                )
        if conflicts:
            print(f"\n  ⚠️  {len(conflicts)} conflict(s) detected:")
            for name_a, task_a, name_b, task_b in conflicts:
                print(
                    f"     • {name_a}/{task_a.description} ({task_a.time}, {task_a.duration} min)"
                    f" overlaps {name_b}/{task_b.description} ({task_b.time}, {task_b.duration} min)"
                )
        print(f"{'=' * 52}\n")
