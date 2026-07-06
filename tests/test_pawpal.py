from datetime import datetime

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
