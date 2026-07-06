"""
pawpal_system.py

Core logic layer for PawPal+, a smart pet care management system.
Defines the data model (Owner, Pet, Task) and the scheduling engine (Scheduler).

This is a Phase 1 skeleton: attributes and method signatures are final-ish,
but method bodies are stubs (`pass`) to be implemented in later phases.
"""

from dataclasses import dataclass, field
from datetime import datetime
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
        pass

    def is_overdue(self, reference_time: Optional[datetime] = None) -> bool:
        """Return True if scheduled_time has passed and the task isn't completed."""
        pass


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
        pass

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by id. Returns True if a pet was removed."""
        pass

    def get_pet(self, pet_id: str) -> Optional[Pet]:
        """Return the pet with the given id, or None if not found."""
        pass


class Scheduler:
    """
    Manages tasks across all pets: adding/removing tasks, sorting by time,
    detecting scheduling conflicts, surfacing overdue/today's tasks, and
    generating future instances of recurring tasks.
    """

    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a new task to the schedule."""
        pass

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by id. Returns True if a task was removed."""
        pass

    def get_tasks_for_pet(self, pet_id: str) -> List[Task]:
        """Return all tasks belonging to a specific pet."""
        pass

    def get_today_tasks(self, reference_date: Optional[datetime] = None) -> List[Task]:
        """Return all tasks scheduled for today (or the given reference date)."""
        pass

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted chronologically by scheduled_time."""
        pass

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        """
        Return pairs of tasks whose time windows overlap for the same pet
        (e.g. a walk and a vet appointment scheduled at overlapping times).
        """
        pass

    def get_overdue_tasks(self, reference_time: Optional[datetime] = None) -> List[Task]:
        """Return tasks that are overdue (past scheduled_time) and not completed."""
        pass

    def generate_daily_plan(
        self,
        pet_ids: Optional[List[str]] = None,
        available_minutes: int = 60,
        reference_date: Optional[datetime] = None,
    ) -> List[Task]:
        """
        Build an optimized daily plan: select and order tasks for the given
        pets/date so their total duration_minutes fits within
        available_minutes, prioritizing the highest-priority (1-5) tasks
        first. This is a resource-constrained selection problem (0/1
        knapsack: maximize total priority subject to total duration <=
        available_minutes) rather than a simple sort — a naive
        sort-by-priority can skip a cheap high-value task in favor of one
        that doesn't fit.

        Implementation note for later phases: a priority/duration_minutes
        density score will likely outperform raw priority as a greedy
        heuristic; true optimality would need a DP knapsack solution if
        task lists grow large enough to matter.
        """
        pass

    def generate_recurring_instances(self, task: Task, horizon_days: int) -> List[Task]:
        """
        Given a recurring task, generate future Task instances up to
        horizon_days ahead, based on its recurrence_pattern.
        """
        pass


if __name__ == "__main__":
    # Quick manual smoke test placeholder — real CLI demo comes in a later phase.
    print("pawpal_system.py loaded — classes: Owner, Pet, Task, Scheduler, TaskType")
