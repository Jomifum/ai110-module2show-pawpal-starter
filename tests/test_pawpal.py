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


def test_filter_tasks_by_completed_status():
    # Arrange
    scheduler = Scheduler()
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", owner_id="owner-1")
    incomplete_task = Task(
        task_id="task-1",
        pet_id=pet.pet_id,
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    completed_task = Task(
        task_id="task-2",
        pet_id=pet.pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
    )
    scheduler.add_task(incomplete_task)
    scheduler.add_task(completed_task)
    completed_task.mark_complete()

    # Act
    incomplete_results = scheduler.filter_tasks(completed=False)
    completed_results = scheduler.filter_tasks(completed=True)

    # Assert
    assert incomplete_results == [incomplete_task]
    assert completed_results == [completed_task]


def test_filter_tasks_by_pet_id():
    # Arrange
    scheduler = Scheduler()
    pet_a = Pet(pet_id="pet-a", name="Mochi", species="dog", owner_id="owner-1")
    pet_b = Pet(pet_id="pet-b", name="Luna", species="cat", owner_id="owner-1")
    task_a = Task(
        task_id="task-1",
        pet_id=pet_a.pet_id,
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    task_b = Task(
        task_id="task-2",
        pet_id=pet_b.pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
    )
    scheduler.add_task(task_a)
    scheduler.add_task(task_b)

    # Act
    filtered_tasks = scheduler.filter_tasks(pet_id=pet_a.pet_id)

    # Assert
    assert filtered_tasks == [task_a]


def test_filter_tasks_combined_filters():
    # Arrange
    scheduler = Scheduler()
    pet = Pet(pet_id="pet-1", name="Mochi", species="dog", owner_id="owner-1")
    incomplete_task = Task(
        task_id="task-1",
        pet_id=pet.pet_id,
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
    )
    completed_task = Task(
        task_id="task-2",
        pet_id=pet.pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
    )
    scheduler.add_task(incomplete_task)
    scheduler.add_task(completed_task)
    completed_task.mark_complete()

    # Act
    filtered_tasks = scheduler.filter_tasks(pet_id=pet.pet_id, completed=False)

    # Assert
    assert filtered_tasks == [incomplete_task]


def test_unsupported_recurrence_pattern_creates_nothing():
    # Arrange
    scheduler = Scheduler()
    task = Task(
        task_id="task-monthly",
        pet_id="pet-1",
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 8, 0),
        is_recurring=True,
        recurrence_pattern="monthly",
    )
    scheduler.add_task(task)

    # Act
    next_task = scheduler.complete_task(task.task_id)

    # Assert
    assert next_task is None
    assert len(scheduler.tasks) == 1
    assert task.completed is True


def test_adjacent_tasks_not_flagged_as_conflict():
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
        pet_id="pet-1",
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 5, 9, 30),
        duration_minutes=15,
    )
    scheduler.add_task(first_task)
    scheduler.add_task(second_task)

    # Act
    conflicts = scheduler.detect_conflicts()

    # Assert
    assert (first_task, second_task, "same_pet") not in conflicts


def test_generate_daily_plan_respects_budget_and_maximizes_priority():
    # Arrange
    scheduler = Scheduler()
    pet_id = "pet-1"
    today = datetime(2026, 7, 5, 8, 0)
    short_task = Task(
        task_id="task-1",
        pet_id=pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=today,
        duration_minutes=15,
        priority=4,
    )
    medium_task = Task(
        task_id="task-2",
        pet_id=pet_id,
        task_type=TaskType.WALK,
        scheduled_time=today,
        duration_minutes=30,
        priority=5,
    )
    long_task = Task(
        task_id="task-3",
        pet_id=pet_id,
        task_type=TaskType.MEDICATION,
        scheduled_time=today,
        duration_minutes=45,
        priority=2,
    )
    scheduler.add_task(short_task)
    scheduler.add_task(medium_task)
    scheduler.add_task(long_task)

    # Act
    plan = scheduler.generate_daily_plan(pet_ids=[pet_id], available_minutes=50, reference_date=today)

    # Assert
    assert plan == [short_task, medium_task]
    assert long_task not in plan


def test_find_next_available_slot_skips_overlapping_tasks():
    # Arrange
    scheduler = Scheduler()
    pet_id = "pet-1"
    existing_task = Task(
        task_id="task-1",
        pet_id=pet_id,
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 5, 9, 0),
        duration_minutes=30,
    )
    scheduler.add_task(existing_task)

    # Act
    next_slot = scheduler.find_next_available_slot(pet_id=pet_id, duration_minutes=20, after=datetime(2026, 7, 5, 9, 0))

    # Assert
    assert next_slot == datetime(2026, 7, 5, 9, 30)
