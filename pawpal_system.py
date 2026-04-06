"""
PawPal+ Logic Layer
Core classes for the pet care scheduling system.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str          # "HH:MM" 24-hour format
    duration: int      # minutes
    frequency: str     # e.g. "daily", "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset this task to incomplete status."""
        self.completed = False

    def __str__(self) -> str:
        """Return a human-readable representation of the task."""
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.time} - {self.description} ({self.duration} min, {self.frequency})"


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
        """Return a flat list of (pet, task) tuples for every pet's task."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The 'brain' that retrieves, organizes, and manages tasks across pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with an owner whose pets will be scheduled."""
        self.owner = owner

    def get_schedule(self) -> List[tuple]:
        """Return all (pet_name, task) pairs sorted chronologically by time."""
        all_tasks = [
            (pet.name, task)
            for pet in self.owner.get_pets()
            for task in pet.get_tasks()
        ]
        return sorted(all_tasks, key=lambda x: x[1].time)

    def get_tasks_by_time(self, time: str) -> List[tuple]:
        """Return all tasks scheduled at a specific time (HH:MM)."""
        return [(name, task) for name, task in self.get_schedule() if task.time == time]

    def get_pending_tasks(self) -> List[tuple]:
        """Return only the tasks that have not yet been completed."""
        return [(name, task) for name, task in self.get_schedule() if not task.completed]

    def mark_task_complete(self, pet_name: str, description: str) -> bool:
        """Mark a specific task complete by pet name and description; returns True on success."""
        for pet in self.owner.get_pets():
            if pet.name == pet_name:
                for task in pet.get_tasks():
                    if task.description == description:
                        task.mark_complete()
                        return True
        return False

    def print_schedule(self) -> None:
        """Print a formatted today's schedule to the terminal."""
        schedule = self.get_schedule()
        print(f"\n{'=' * 50}")
        print(f"  Today's Schedule for {self.owner.name}")
        print(f"{'=' * 50}")
        if not schedule:
            print("  No tasks scheduled.")
        else:
            for pet_name, task in schedule:
                status = "✓" if task.completed else "○"
                print(
                    f"  [{status}] {task.time}  |  {pet_name:<12}|  "
                    f"{task.description} ({task.duration} min)"
                )
        print(f"{'=' * 50}\n")
