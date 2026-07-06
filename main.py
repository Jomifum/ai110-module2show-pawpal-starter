from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType

TASK_TYPE_EMOJIS = {
    TaskType.FEEDING: "🍽️",
    TaskType.WALK: "🐾",
    TaskType.MEDICATION: "💊",
    TaskType.APPOINTMENT: "🏥",
}


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
        Task("task5", pet1.pet_id, TaskType.MEDICATION, today + timedelta(hours=4), duration_minutes=10, priority=2),
        Task("task6", pet2.pet_id, TaskType.WALK, today + timedelta(hours=0, minutes=30), duration_minutes=25, priority=1),
    ]

    scheduler = Scheduler()
    for task in tasks:
        scheduler.add_task(task)

    recurring_task = Task(
        "task7",
        pet1.pet_id,
        TaskType.FEEDING,
        today + timedelta(hours=2),
        duration_minutes=10,
        priority=4,
        is_recurring=True,
        recurrence_pattern="daily",
    )
    scheduler.add_task(recurring_task)

    print("Task List Before Completion")
    print("=" * 40)
    for task in scheduler.sort_by_time():
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else task.pet_id
        print(
            f"- {TASK_TYPE_EMOJIS[task.task_type]} {pet_name}: {task.task_type.value.title()} | "
            f"{task.scheduled_time.strftime('%H:%M')} | "
            f"{task.duration_minutes} min | priority {task.priority}"
        )

    new_task = scheduler.complete_task(recurring_task.task_id)
    print("\nTask List After Completion")
    print("=" * 40)
    for task in scheduler.sort_by_time():
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else task.pet_id
        print(
            f"- {TASK_TYPE_EMOJIS[task.task_type]} {pet_name}: {task.task_type.value.title()} | "
            f"{task.scheduled_time.strftime('%H:%M')} | "
            f"{task.duration_minutes} min | priority {task.priority}"
        )

    print("\nCompleted Recurring Task")
    print("=" * 40)
    if new_task is not None:
        print(f"- New task added: {new_task.task_id} at {new_task.scheduled_time.strftime('%H:%M')}")
    else:
        print("- No new task created.")

    print("\nToday's Schedule")
    print("=" * 40)
    for task in scheduler.sort_by_time():
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else task.pet_id
        print(
            f"- {TASK_TYPE_EMOJIS[task.task_type]} {pet_name}: {task.task_type.value.title()} | "
            f"{task.scheduled_time.strftime('%H:%M')} | "
            f"{task.duration_minutes} min | priority {task.priority}"
        )

    print("\nSorted Tasks")
    print("=" * 40)
    for task in scheduler.sort_by_time():
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else task.pet_id
        print(
            f"- {TASK_TYPE_EMOJIS[task.task_type]} {pet_name}: {task.task_type.value.title()} | "
            f"{task.scheduled_time.strftime('%H:%M')} | "
            f"{task.duration_minutes} min | priority {task.priority}"
        )

    print("\nIncomplete Tasks")
    print("=" * 40)
    for task in scheduler.filter_tasks(completed=False):
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else task.pet_id
        print(
            f"- {TASK_TYPE_EMOJIS[task.task_type]} {pet_name}: {task.task_type.value.title()} | "
            f"{task.scheduled_time.strftime('%H:%M')} | "
            f"{task.duration_minutes} min | priority {task.priority}"
        )

    print("\nTasks for One Pet")
    print("=" * 40)
    for task in scheduler.filter_tasks(pet_id=pet1.pet_id):
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else task.pet_id
        print(
            f"- {TASK_TYPE_EMOJIS[task.task_type]} {pet_name}: {task.task_type.value.title()} | "
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
            f"- {TASK_TYPE_EMOJIS[task.task_type]} {pet_name}: {task.task_type.value.title()} | "
            f"{task.scheduled_time.strftime('%H:%M')} | "
            f"{task.duration_minutes} min | priority {task.priority}"
        )

    print("\nConflicts")
    print("=" * 40)
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for first, second, _ in conflicts:
            print(f"- {first.task_id} and {second.task_id} overlap")
    else:
        print("No conflicts found.")

    print("\nNext Available Slot")
    print("=" * 40)
    next_slot = scheduler.find_next_available_slot(pet_id=pet1.pet_id, duration_minutes=20, after=today)
    if next_slot is not None:
        print(f"- Earliest open slot: {next_slot.strftime('%H:%M')}")
    else:
        print("- No open slot found.")


if __name__ == "__main__":
    main()
