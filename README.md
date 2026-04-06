# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

---

## Features

### Core scheduling
- **Chronological sorting** — Tasks are always displayed in `HH:MM` time order using Python's `sorted()` with a lambda key, regardless of the order they were added.
- **Task completion tracking** — Mark individual tasks done; a progress bar shows how many of the day's tasks are finished.

### Smart algorithms
- **Recurring tasks** — Daily tasks automatically generate a next-occurrence copy (due tomorrow) when marked complete; weekly tasks generate a copy due in 7 days. One-off (`once`) tasks do not recur. Uses Python's `datetime.timedelta` for accurate date calculation.
- **Conflict detection** — The Scheduler checks every pair of scheduled tasks for **interval overlap** (`start_A < end_B and start_B < end_A`). Conflicting tasks are surfaced as `⚠️ st.warning` banners in the UI so the owner can reschedule before the day starts.

### Filtering
- **Filter by pet** — View tasks for a single pet or across all pets.
- **Filter by status** — Show only pending, only completed, or all tasks.

### UI
- **Streamlit session state** — The `Owner` object (and all its pets/tasks) lives in `st.session_state`, so data persists across button clicks and re-runs without being reset.
- **Conflict warnings** — Displayed prominently at the top of the schedule tab with full details (pet name, task name, time, duration).
- **Per-pet task tables** — Expandable sections in the Add Tasks tab show each pet's current tasks sorted by time.

---

## Project structure

```
├── app.py               # Streamlit UI (connects to logic layer)
├── pawpal_system.py     # Logic layer: Task, Pet, Owner, Scheduler
├── main.py              # Terminal demo / smoke test
├── tests/
│   └── test_pawpal.py  # pytest suite (16 tests)
├── requirements.txt
└── reflection.md        # Design & AI-collaboration reflection
```

---

## Getting started

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the terminal demo

```bash
python3 main.py
```

### Run tests

```bash
python3 -m pytest
```

---

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
  <img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

---

## Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
