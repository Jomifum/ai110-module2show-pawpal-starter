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

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
 Today's Schedule

========================================

- Mochi: Walk | 08:00 | 30 min | priority 5

- Mochi: Feeding | 09:00 | 15 min | priority 4

- Luna: Medication | 10:00 | 20 min | priority 3

- Luna: Appointment | 11:00 | 45 min | priority 2

Daily Plan

========================================

- Mochi: Feeding | 09:00 | 15 min | priority 4

- Mochi: Walk | 08:00 | 30 min | priority 5

- Luna: Medication | 10:00 | 20 min | priority 3

Conflicts

========================================

No conflicts found.           
```

## 🧪 Testing PawPal+

Run the test suite with:

```bash
python -m pytest
```

The current suite covers core class behavior such as task completion and pet/task management, chronological sorting, filtering by pet, by completion status, and by both conditions together, recurring task completion for daily and weekly intervals plus unsupported patterns correctly creating nothing, and conflict detection for same-pet overlaps, cross-pet double-booking, exact-duplicate-time cases, and adjacent non-overlapping tasks that are correctly not flagged.

## ✨ Features

- Sorting by time: Scheduler.sort_by_time() orders all tasks chronologically by scheduled_time.
- Filtering by pet and/or completion status: Scheduler.filter_tasks() returns tasks filtered by pet_id and/or completed state.
- Conflict detection: Scheduler.detect_conflicts() flags same-pet overlaps and cross-pet owner double-booking conflicts with tagged results.
- Recurring task automation: Scheduler.complete_task() marks a task complete and creates the next daily or weekly occurrence when appropriate.
- Time-budget-optimized daily planning: Scheduler.generate_daily_plan() selects a set of tasks that fits the available_minutes budget while prioritizing higher-value work.

CLI output uses emoji indicators per task type (🍽️ feeding, 🐾 walk, 💊 medication, 🏥 appointment) implemented via a plain dict lookup in main.py, with no external library required.

## 🎬 Demo Walkthrough

1. Open the Streamlit UI and create an owner account, then add one or more pets to the owner profile.
2. Schedule tasks for a pet by choosing a pet, task type, time, duration, and priority.
3. View the schedule section to see tasks ordered by time, the optimized daily plan section to see which tasks fit the current time budget, and the conflict section to see any overlap warnings.
4. Example workflow: add a pet, schedule two tasks for the same pet at overlapping times, then view today's schedule and see a conflict warning appear for the overlap.
5. The workflow demonstrates Scheduler.sort_by_time(), Scheduler.generate_daily_plan(), Scheduler.detect_conflicts(), and the UI's task filtering controls for pet and incomplete-task views.

Example CLI output from main.py:

```bash
# Paste real output from python main.py here
```
