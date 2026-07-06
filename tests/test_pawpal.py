from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType


def test_mark_complete():
    # Arrange
    task = Task(
        task_id="task-1",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )

    # Act
    task.mark_complete()

    # Assert
    assert task.completed is True


def test_add_pet_increases_task_count():
    # Arrange
    owner = Owner(owner_id="owner-1", name="Jordan", email="jordan@example.com")
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", owner_id=owner.owner_id)
    owner.add_pet(pet)

    scheduler = Scheduler()
    task_one = Task(
        task_id="task-1",
        pet_id=pet.pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    task_two = Task(
        task_id="task-2",
        pet_id=pet.pet_id,
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
    )

    # Act
    scheduler.add_task(task_one)
    scheduler.add_task(task_two)

    # Assert
    assert len(scheduler.get_tasks_for_pet(pet.pet_id)) == 2


def test_detect_conflicts_returns_same_pet_overlap():
    # Arrange
    scheduler = Scheduler()
    first_task = Task(
        task_id="task-1",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
        duration_minutes=30,
    )
    second_task = Task(
        task_id="task-2",
        pet_id="pet-1",
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 8, 15),
        duration_minutes=20,
    )
    scheduler.add_task(first_task)
    scheduler.add_task(second_task)

    # Act
    conflicts = scheduler.detect_conflicts()

    # Assert
    assert conflicts == [(first_task, second_task, "same_pet")]


def test_detect_conflicts_returns_owner_double_booked_for_different_pets():
    # Arrange
    scheduler = Scheduler()
    first_task = Task(
        task_id="task-1",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
        duration_minutes=30,
    )
    second_task = Task(
        task_id="task-2",
        pet_id="pet-2",
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 9, 15),
        duration_minutes=20,
    )
    scheduler.add_task(first_task)
    scheduler.add_task(second_task)

    # Act
    conflicts = scheduler.detect_conflicts()

    # Assert
    assert conflicts == [(first_task, second_task, "owner_double_booked")]


def test_sort_by_time_chronological_order():
    # Arrange
    scheduler = Scheduler()
    first_task = Task(
        task_id="task-1",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 10, 0),
    )
    second_task = Task(
        task_id="task-2",
        pet_id="pet-1",
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    third_task = Task(
        task_id="task-3",
        pet_id="pet-1",
        task_type=TaskType.MEDICATION,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
    )
    scheduler.add_task(first_task)
    scheduler.add_task(second_task)
    scheduler.add_task(third_task)

    # Act
    sorted_tasks = scheduler.sort_by_time()
    sorted_times = [task.scheduled_time for task in sorted_tasks]

    # Assert
    assert all(
        current_time <= next_time
        for current_time, next_time in zip(sorted_times, sorted_times[1:])
    )


def test_recurring_daily_creates_next_occurrence():
    # Arrange
    scheduler = Scheduler()
    original_time = datetime(2026, 7, 5, 8, 0)
    task = Task(
        task_id="task-daily",
        pet_id="pet-1",
        task_type=TaskType.FEEDING,
        scheduled_time=original_time,
        is_recurring=True,
        recurrence_pattern="daily",
    )
    scheduler.add_task(task)

    # Act
    next_task = scheduler.complete_task(task.task_id)

    # Assert
    assert next_task is not None
    assert next_task.scheduled_time == original_time + timedelta(days=1)
    assert any(existing_task.task_id == next_task.task_id for existing_task in scheduler.tasks)
    assert next_task.completed is False


def test_recurring_weekly_creates_next_occurrence():
    # Arrange
    scheduler = Scheduler()
    original_time = datetime(2026, 7, 5, 8, 0)
    task = Task(
        task_id="task-weekly",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=original_time,
        is_recurring=True,
        recurrence_pattern="weekly",
    )
    scheduler.add_task(task)

    # Act
    next_task = scheduler.complete_task(task.task_id)

    # Assert
    assert next_task is not None
    assert next_task.scheduled_time == original_time + timedelta(days=7)
    assert any(existing_task.task_id == next_task.task_id for existing_task in scheduler.tasks)
    assert next_task.completed is False


def test_detect_conflicts_flags_duplicate_time_same_pet():
    # Arrange
    scheduler = Scheduler()
    first_task = Task(
        task_id="task-1",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    second_task = Task(
        task_id="task-2",
        pet_id="pet-1",
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    scheduler.add_task(first_task)
    scheduler.add_task(second_task)

    # Act
    conflicts = scheduler.detect_conflicts()

    # Assert
    assert conflicts == [(first_task, second_task, "same_pet")]


def test_detect_conflicts_owner_double_booked():
    # Arrange
    owner = Owner(owner_id="owner-1", name="Jordan", email="jordan@example.com")
    first_pet = Pet(pet_id="pet-1", name="Mochi", species="dog", owner_id=owner.owner_id)
    second_pet = Pet(pet_id="pet-2", name="Milo", species="cat", owner_id=owner.owner_id)
    owner.add_pet(first_pet)
    owner.add_pet(second_pet)

    scheduler = Scheduler()
    first_task = Task(
        task_id="task-1",
        pet_id=first_pet.pet_id,
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
    )
    second_task = Task(
        task_id="task-2",
        pet_id=second_pet.pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
    )
    scheduler.add_task(first_task)
    scheduler.add_task(second_task)

    # Act
    conflicts = scheduler.detect_conflicts()

    # Assert
    assert conflicts == [(first_task, second_task, "owner_double_booked")]


def test_filter_tasks_no_args_returns_all():
    # Arrange
    scheduler = Scheduler()
    first_task = Task(
        task_id="task-1",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    second_task = Task(
        task_id="task-2",
        pet_id="pet-2",
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
    )
    scheduler.add_task(first_task)
    scheduler.add_task(second_task)

    # Act
    filtered_tasks = scheduler.filter_tasks()

    # Assert
    assert filtered_tasks == [first_task, second_task]


def test_pet_with_no_tasks():
    # Arrange
    scheduler = Scheduler()
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", owner_id="owner-1")

    # Act
    tasks_for_pet = scheduler.get_tasks_for_pet(pet.pet_id)

    # Assert
    assert tasks_for_pet == []


def test_non_recurring_task_completion_creates_nothing():
    # Arrange
    scheduler = Scheduler()
    task = Task(
        task_id="task-1",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    scheduler.add_task(task)

    # Act
    next_task = scheduler.complete_task(task.task_id)

    # Assert
    assert next_task is None
    assert task.completed is True
