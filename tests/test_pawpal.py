"""
tests/test_pawpal.py — Unit tests for PawPal+ core classes.
Run with: python3 -m pytest
"""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_scheduler(*pets: Pet, owner_name: str = "Jordan") -> Scheduler:
    """Convenience: build an Owner + Scheduler with the supplied pets."""
    owner = Owner(owner_name)
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


# ─── Task tests ───────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = Task("Morning walk", "07:00", 30, "daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_reset_clears_completed_status():
    """reset() should restore completed to False after mark_complete()."""
    task = Task("Evening walk", "18:00", 30, "daily")
    task.mark_complete()
    task.reset()
    assert task.completed is False


# ─── Pet tests ────────────────────────────────────────────────────────────────

def test_add_task_increases_count():
    """Adding tasks should increase the pet's task count by one each time."""
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk", "07:00", 30, "daily"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task("Evening walk", "18:00", 30, "daily"))
    assert len(pet.get_tasks()) == 2


def test_remove_task_decreases_count():
    """remove_task() should delete the matching task by description."""
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Morning feeding", "08:00", 5, "daily"))
    pet.add_task(Task("Playtime", "17:00", 15, "daily"))
    removed = pet.remove_task("Playtime")
    assert removed is True
    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0].description == "Morning feeding"


def test_remove_nonexistent_task_returns_false():
    """remove_task() should return False when no matching task is found."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", "07:00", 30, "daily"))
    result = pet.remove_task("Nonexistent task")
    assert result is False
    assert len(pet.get_tasks()) == 1


# ─── Scheduler — sorting ─────────────────────────────────────────────────────

def test_scheduler_sorts_by_time():
    """get_schedule() should return tasks in chronological order regardless of insertion order."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Evening walk",  "18:00", 30, "daily"))
    pet.add_task(Task("Morning walk",  "07:00", 30, "daily"))
    pet.add_task(Task("Afternoon nap", "13:00", 20, "once"))

    scheduler = make_scheduler(pet)
    times = [task.time for _, task in scheduler.get_schedule()]
    assert times == sorted(times)


# ─── Scheduler — mark complete & recurrence ───────────────────────────────────

def test_scheduler_mark_task_complete():
    """mark_task_complete() should mark the right task and return True."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", "07:00", 30, "daily"))
    scheduler = make_scheduler(pet)

    result = scheduler.mark_task_complete("Mochi", "Morning walk")
    assert result is True
    assert pet.get_tasks()[0].completed is True


def test_mark_unknown_task_returns_false():
    """mark_task_complete() should return False when the task is not found."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", "07:00", 30, "daily"))
    scheduler = make_scheduler(pet)

    result = scheduler.mark_task_complete("Mochi", "Nonexistent")
    assert result is False


def test_daily_recurrence_creates_next_task():
    """Completing a daily task should add a new task due tomorrow."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", "07:00", 30, "daily"))
    scheduler = make_scheduler(pet)

    scheduler.mark_task_complete("Mochi", "Morning walk")

    tasks = pet.get_tasks()
    assert len(tasks) == 2, "A next-occurrence task should have been appended"

    next_task = tasks[1]
    assert next_task.completed is False
    assert next_task.description == "Morning walk"
    expected_date = (date.today() + timedelta(days=1)).isoformat()
    assert next_task.due_date == expected_date


def test_weekly_recurrence_creates_next_task():
    """Completing a weekly task should add a new task due in 7 days."""
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Grooming", "10:00", 45, "weekly"))
    scheduler = make_scheduler(pet)

    scheduler.mark_task_complete("Luna", "Grooming")

    tasks = pet.get_tasks()
    assert len(tasks) == 2
    expected_date = (date.today() + timedelta(weeks=1)).isoformat()
    assert tasks[1].due_date == expected_date


def test_once_task_does_not_recur():
    """Completing a 'once' task should NOT create a follow-up task."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Vet visit", "09:00", 60, "once"))
    scheduler = make_scheduler(pet)

    scheduler.mark_task_complete("Mochi", "Vet visit")

    assert len(pet.get_tasks()) == 1


# ─── Scheduler — filtering ────────────────────────────────────────────────────

def test_pending_tasks_excludes_completed():
    """get_pending_tasks() should not include completed tasks."""
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Morning feeding", "08:00", 5, "daily"))
    pet.add_task(Task("Playtime", "17:00", 15, "daily"))
    scheduler = make_scheduler(pet)

    scheduler.mark_task_complete("Luna", "Morning feeding")
    pending = scheduler.get_pending_tasks()

    assert len(pending) == 1
    # The next-occurrence task (tomorrow) shouldn't show as pending yet — it's undated
    assert pending[0][1].description == "Playtime"


def test_filter_by_pet_name():
    """filter_tasks(pet_name=...) should only return tasks for that pet."""
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Morning walk", "07:00", 30, "daily"))
    luna = Pet("Luna", "cat")
    luna.add_task(Task("Morning feeding", "08:00", 5, "daily"))

    scheduler = make_scheduler(mochi, luna)
    results = scheduler.filter_tasks(pet_name="Luna")

    assert all(name == "Luna" for name, _ in results)
    assert len(results) == 1


def test_filter_by_completed_status():
    """filter_tasks(completed=True/False) should respect the status flag."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", "07:00", 30, "daily"))
    pet.add_task(Task("Evening walk", "18:00", 30, "daily"))
    scheduler = make_scheduler(pet)

    scheduler.mark_task_complete("Mochi", "Morning walk")

    done = scheduler.filter_tasks(completed=True)
    pending = scheduler.filter_tasks(completed=False)

    # done includes the original completed task (next occurrence is not complete)
    assert any(t.description == "Morning walk" and t.completed for _, t in done)
    assert all(not t.completed for _, t in pending)


# ─── Scheduler — conflict detection ──────────────────────────────────────────

def test_conflict_detected_for_overlapping_tasks():
    """Tasks whose time windows overlap should be flagged as conflicts."""
    pet = Pet("Mochi", "dog")
    # 08:00 for 30 min → ends 08:30
    pet.add_task(Task("Morning walk",   "08:00", 30, "daily"))
    # 08:20 for 20 min → ends 08:40 — overlaps with morning walk
    pet.add_task(Task("Vet appointment", "08:20", 20, "once"))

    scheduler = make_scheduler(pet)
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) >= 1
    descriptions = {task.description for _, task, *_ in [(c[0], c[1]) for c in conflicts]}
    assert "Morning walk" in descriptions or "Vet appointment" in descriptions


def test_no_conflict_for_sequential_tasks():
    """Tasks that end exactly when the next one starts should NOT conflict."""
    pet = Pet("Mochi", "dog")
    # 07:00 for 30 min → ends 07:30
    pet.add_task(Task("Morning walk", "07:00", 30, "daily"))
    # 07:30 for 10 min → starts right after — no overlap
    pet.add_task(Task("Breakfast",    "07:30", 10, "daily"))

    scheduler = make_scheduler(pet)
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) == 0


def test_conflict_detected_across_different_pets():
    """Overlapping tasks from different pets should also be flagged."""
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Walk",    "09:00", 30, "daily"))  # 09:00 – 09:30
    luna = Pet("Luna", "cat")
    luna.add_task(Task("Grooming", "09:15", 20, "once"))   # 09:15 – 09:35

    scheduler = make_scheduler(mochi, luna)
    conflicts = scheduler.get_conflicts()

    assert len(conflicts) >= 1
