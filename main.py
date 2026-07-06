from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType


def main() -> None:
    owner = Owner(owner_id="owner1", name="Jordan", email="jordan@example.com", available_minutes_per_day=90)

    pet1 = Pet(pet_id="pet1", name="Mochi", species="dog", owner_id=owner.owner_id)
    pet2 = Pet(pet_id="pet2", name="Luna", species="cat", owner_id=owner.owner_id)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    today = datetime(2026, 7, 5, 8, 0)
    tasks = [
        Task("task1", pet1.pet_id, TaskType.WALK, today + timedelta(hours=0), duration_minutes=30, priority=5),
        Task("task2", pet1.pet_id, TaskType.FEEDING, today + timedelta(hours=1), duration_minutes=15, priority=4),
        Task("task3", pet2.pet_id, TaskType.MEDICATION, today + timedelta(hours=2), duration_minutes=20, priority=3),
        Task("task4", pet2.pet_id, TaskType.APPOINTMENT, today + timedelta(hours=3), duration_minutes=45, priority=2),
    ]

    scheduler = Scheduler()
    for task in tasks:
        scheduler.add_task(task)

    print("Today's Schedule")
    print("=" * 40)
    for task in scheduler.sort_by_time():
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else task.pet_id
        print(
            f"- {pet_name}: {task.task_type.value.title()} | "
            f"{task.scheduled_time.strftime('%H:%M')} | "
            f"{task.duration_minutes} min | priority {task.priority}"
        )

    print("\nDaily Plan")
    print("=" * 40)
    for task in scheduler.generate_daily_plan(
        pet_ids=[pet.pet_id for pet in owner.pets],
        available_minutes=owner.available_minutes_per_day,
        reference_date=today,
    ):
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else task.pet_id
        print(
            f"- {pet_name}: {task.task_type.value.title()} | "
            f"{task.scheduled_time.strftime('%H:%M')} | "
            f"{task.duration_minutes} min | priority {task.priority}"
        )

    print("\nConflicts")
    print("=" * 40)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for first, second in conflicts:
            print(f"- {first.task_id} and {second.task_id} overlap")
    else:
        print("No conflicts found.")


if __name__ == "__main__":
    main()
