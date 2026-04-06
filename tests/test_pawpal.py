"""
tests/test_pawpal.py — Unit tests for PawPal+ core classes.
Run with: python -m pytest
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ─── Task tests ──────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = Task("Morning walk", "07:00", 30, "daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_reset_clears_completed_status():
    """reset() should set completed back to False after mark_complete()."""
    task = Task("Evening walk", "18:00", 30, "daily")
    task.mark_complete()
    task.reset()
    assert task.completed is False


# ─── Pet tests ────────────────────────────────────────────────────────────────

def test_add_task_increases_count():
    """Adding tasks to a Pet should increase its task count correctly."""
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


# ─── Scheduler tests ──────────────────────────────────────────────────────────

def test_scheduler_sorts_by_time():
    """get_schedule() should return tasks in chronological order."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Evening walk",  "18:00", 30, "daily"))
    pet.add_task(Task("Morning walk",  "07:00", 30, "daily"))
    pet.add_task(Task("Afternoon nap", "13:00", 20, "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    schedule = scheduler.get_schedule()
    times = [task.time for _, task in schedule]
    assert times == sorted(times)


def test_scheduler_mark_task_complete():
    """mark_task_complete() should complete the right task and return True."""
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", "07:00", 30, "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    result = scheduler.mark_task_complete("Mochi", "Morning walk")
    assert result is True
    assert pet.get_tasks()[0].completed is True


def test_scheduler_pending_tasks_excludes_completed():
    """get_pending_tasks() should not include completed tasks."""
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Morning feeding", "08:00",  5, "daily"))
    pet.add_task(Task("Playtime",        "17:00", 15, "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete("Luna", "Morning feeding")
    pending = scheduler.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0][1].description == "Playtime"
