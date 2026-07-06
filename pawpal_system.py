"""
pawpal_system.py

Core logic layer for PawPal+, a smart pet care management system.
Defines the data model (Owner, Pet, Task) and the scheduling engine (Scheduler).

This is a Phase 1 skeleton: attributes and method signatures are final-ish,
but method bodies are stubs (`pass`) to be implemented in later phases.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple


class TaskType(Enum):
    """Category of pet-care task."""
    FEEDING = "feeding"
    WALK = "walk"
    MEDICATION = "medication"
    APPOINTMENT = "appointment"


@dataclass
class Pet:
    """A single pet belonging to an Owner."""
    pet_id: str
    name: str
    species: str
    owner_id: str
    breed: str = ""
    age: int = 0
    weight: float = 0.0
    medical_notes: str = ""


@dataclass
class Task:
    """A single scheduled care task (feeding, walk, medication, or appointment)."""
    task_id: str
    pet_id: str
    task_type: TaskType
    scheduled_time: datetime
    duration_minutes: int = 15
    priority: int = 1  # 1 (low) to 5 (critical) - drives ordering in generate_daily_plan
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # e.g. "daily", "weekly"
    completed: bool = False
    notes: str = ""

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_overdue(self, reference_time: Optional[datetime] = None) -> bool:
        """Return True if scheduled_time has passed and the task isn't completed."""
        if reference_time is None:
            reference_time = datetime.now()
        return self.scheduled_time < reference_time and not self.completed


@dataclass
class Owner:
    """A pet owner/user of the app, who can have multiple pets."""
    owner_id: str
    name: str
    email: str
    phone: str = ""
    available_minutes_per_day: int = 60  # time budget owner has for pet care each day
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        if not any(existing_pet.pet_id == pet.pet_id for existing_pet in self.pets):
            self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by id. Returns True if a pet was removed."""
        original_length = len(self.pets)
        self.pets = [existing_pet for existing_pet in self.pets if existing_pet.pet_id != pet_id]
        return len(self.pets) < original_length

    def get_pet(self, pet_id: str) -> Optional[Pet]:
        """Return the pet with the given id, or None if not found."""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None


class Scheduler:
    """
    Manages tasks across all pets: adding/removing tasks, sorting by time,
    detecting scheduling conflicts, surfacing overdue/today's tasks, and
    generating future instances of recurring tasks.
    """

    def __init__(self) -> None:
        """Initialize an empty scheduler instance."""
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a new task to the schedule."""
        if not any(existing_task.task_id == task.task_id for existing_task in self.tasks):
            self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by id. Returns True if a task was removed."""
        original_length = len(self.tasks)
        self.tasks = [existing_task for existing_task in self.tasks if existing_task.task_id != task_id]
        return len(self.tasks) < original_length

    def get_tasks_for_pet(self, pet_id: str) -> List[Task]:
        """Return all tasks belonging to a specific pet."""
        return [task for task in self.tasks if task.pet_id == pet_id]

    def get_today_tasks(self, reference_date: Optional[datetime] = None) -> List[Task]:
        """Return all tasks scheduled for today (or the given reference date)."""
        if reference_date is None:
            reference_date = datetime.now()
        target_date = reference_date.date()
        return [task for task in self.tasks if task.scheduled_time.date() == target_date]

    def filter_tasks(self, pet_id: str = None, completed: bool = None) -> List[Task]:
        """Return tasks filtered by pet and/or completion status."""
        return [
            task
            for task in self.tasks
            if (pet_id is None or task.pet_id == pet_id)
            and (completed is None or task.completed is completed)
        ]

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted chronologically by scheduled_time."""
        return sorted(self.tasks, key=lambda task: task.scheduled_time)

    def detect_conflicts(self) -> List[Tuple[Task, Task, str]]:
        """Return overlapping task pairs with a conflict type label."""
        conflicts: List[Tuple[Task, Task, str]] = []
        for index, first_task in enumerate(self.tasks):
            for second_task in self.tasks[index + 1 :]:
                first_end = first_task.scheduled_time + timedelta(minutes=first_task.duration_minutes)
                second_end = second_task.scheduled_time + timedelta(minutes=second_task.duration_minutes)

                if first_task.scheduled_time < second_end and second_task.scheduled_time < first_end:
                    if first_task.pet_id == second_task.pet_id:
                        conflicts.append((first_task, second_task, "same_pet"))
                    else:
                        conflicts.append((first_task, second_task, "owner_double_booked"))
        return conflicts

    def get_overdue_tasks(self, reference_time: Optional[datetime] = None) -> List[Task]:
        """Return tasks that are overdue (past scheduled_time) and not completed."""
        return [task for task in self.tasks if task.is_overdue(reference_time)]

    def generate_daily_plan(
        self,
        pet_ids: Optional[List[str]] = None,
        available_minutes: int = 60,
        reference_date: Optional[datetime] = None,
    ) -> List[Task]:
        """Build a daily plan that fits the available minutes while favoring higher-value tasks."""
        if available_minutes <= 0:
            return []

        if reference_date is None:
            reference_date = datetime.now()
        target_date = reference_date.date()

        candidate_tasks = [
            task
            for task in self.tasks
            if not task.completed
            and task.scheduled_time.date() == target_date
            and (pet_ids is None or task.pet_id in pet_ids)
        ]

        candidate_tasks = sorted(
            candidate_tasks,
            key=lambda task: (
                -(task.priority / max(task.duration_minutes, 1)),
                task.scheduled_time,
                task.task_id,
            ),
        )

        selected_tasks: List[Task] = []
        total_duration = 0
        for task in candidate_tasks:
            if total_duration + task.duration_minutes <= available_minutes:
                selected_tasks.append(task)
                total_duration += task.duration_minutes

        return selected_tasks

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task complete and create the next recurring instance if needed."""
        task = next((existing_task for existing_task in self.tasks if existing_task.task_id == task_id), None)
        if task is None:
            return None

        task.mark_complete()

        if not task.is_recurring or task.recurrence_pattern not in {"daily", "weekly"}:
            return None

        step_days = 1 if task.recurrence_pattern == "daily" else 7
        next_task = Task(
            task_id=f"{task.task_id}_next",
            pet_id=task.pet_id,
            task_type=task.task_type,
            scheduled_time=task.scheduled_time + timedelta(days=step_days),
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            is_recurring=task.is_recurring,
            recurrence_pattern=task.recurrence_pattern,
            completed=False,
            notes=task.notes,
        )
        self.add_task(next_task)
        return next_task

    def generate_recurring_instances(self, task: Task, horizon_days: int) -> List[Task]:
        """Generate future instances of a recurring task up to the given horizon."""
        if horizon_days <= 0:
            return []

        pattern = task.recurrence_pattern
        if pattern not in {"daily", "weekly"}:
            return []

        instances: List[Task] = []
        step_days = 1 if pattern == "daily" else 7
        current_offset = step_days
        while current_offset <= horizon_days:
            instances.append(
                Task(
                    task_id=f"{task.task_id}_{current_offset}",
                    pet_id=task.pet_id,
                    task_type=task.task_type,
                    scheduled_time=task.scheduled_time + timedelta(days=current_offset),
                    duration_minutes=task.duration_minutes,
                    priority=task.priority,
                    is_recurring=task.is_recurring,
                    recurrence_pattern=task.recurrence_pattern,
                    completed=False,
                    notes=task.notes,
                )
            )
            current_offset += step_days

        return instances


if __name__ == "__main__":
    # Quick manual smoke test placeholder — real CLI demo comes in a later phase.
    print("pawpal_system.py loaded — classes: Owner, Pet, Task, Scheduler, TaskType")
