from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

if "owner" not in st.session_state:
    st.session_state.owner = None

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input("Available minutes per day", min_value=1, max_value=1440, value=90)

if st.session_state.owner is not None:
    owner = st.session_state.owner
    st.success(f"Owner ready: {owner.name} ({owner.available_minutes_per_day} min/day)")
else:
    if st.button("Create Owner"):
        if owner_name.strip():
            owner_id = f"owner-{len(st.session_state.scheduler.tasks) + 1}"
            st.session_state.owner = Owner(
                owner_id=owner_id,
                name=owner_name.strip(),
                email="placeholder@example.com",
                available_minutes_per_day=int(available_minutes),
            )
            st.rerun()
        else:
            st.warning("Please enter an owner name first.")

if st.session_state.owner is not None:
    with st.form("add_pet_form"):
        st.subheader("Add a Pet")
        pet_name = st.text_input("Pet name", value="Mochi")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        breed = st.text_input("Breed", value="")
        age = st.number_input("Age", min_value=0, max_value=50, value=0)
        weight = st.number_input("Weight", min_value=0.0, max_value=200.0, value=0.0)

        submitted = st.form_submit_button("Add Pet")
        if submitted:
            if pet_name.strip():
                pet_id = f"pet-{len(st.session_state.owner.pets) + 1}"
                pet = Pet(
                    pet_id=pet_id,
                    name=pet_name.strip(),
                    species=species,
                    owner_id=st.session_state.owner.owner_id,
                    breed=breed.strip(),
                    age=int(age),
                    weight=float(weight),
                )
                st.session_state.owner.add_pet(pet)
                st.success(f"Added {pet.name} to {st.session_state.owner.name}'s account.")
                st.rerun()
            else:
                st.warning("Please enter a pet name first.")

    if st.session_state.owner.pets:
        st.write("Current pets:")
        for pet in st.session_state.owner.pets:
            st.write(f"- {pet.name} ({pet.species})")

    if st.session_state.owner.pets:
        with st.form("schedule_task_form"):
            st.subheader("Schedule a Task")
            pet_options = [(pet.name, pet.pet_id) for pet in st.session_state.owner.pets]
            selected_pet_name = st.selectbox("Pet", options=[name for name, _ in pet_options])
            selected_pet_id = next(pet_id for name, pet_id in pet_options if name == selected_pet_name)

            task_type = st.selectbox("Task Type", options=[task_type.value for task_type in TaskType])
            scheduled_time = st.time_input("Scheduled Time")
            duration_minutes = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.slider("Priority", min_value=1, max_value=5, value=3)

            submitted = st.form_submit_button("Add Task")
            if submitted:
                task_id = f"task-{len(st.session_state.scheduler.tasks) + 1}"
                task = Task(
                    task_id=task_id,
                    pet_id=selected_pet_id,
                    task_type=TaskType(task_type),
                    scheduled_time=datetime.combine(datetime.today().date(), scheduled_time),
                    duration_minutes=int(duration_minutes),
                    priority=int(priority),
                )
                st.session_state.scheduler.add_task(task)
                st.success(f"Added {task.task_type.value} task for {selected_pet_name}.")
                st.rerun()

    if st.session_state.owner is not None and st.session_state.owner.pets:
        st.subheader("Today's Schedule")

        pet_filter_options = ["All pets"] + [pet.name for pet in st.session_state.owner.pets]
        selected_pet_name = st.selectbox("Filter by pet", options=pet_filter_options)
        show_incomplete_only = st.checkbox("Show incomplete tasks only", value=True)

        selected_pet_id = None
        if selected_pet_name != "All pets":
            selected_pet_id = next(
                pet.pet_id for pet in st.session_state.owner.pets if pet.name == selected_pet_name
            )

        filtered_tasks = st.session_state.scheduler.filter_tasks(
            pet_id=selected_pet_id,
            completed=False if show_incomplete_only else None,
        )
        sorted_tasks = sorted(filtered_tasks, key=lambda task: task.scheduled_time)

        if sorted_tasks:
            schedule_rows = []
            for task in sorted_tasks:
                pet = st.session_state.owner.get_pet(task.pet_id)
                pet_name = pet.name if pet else task.pet_id
                schedule_rows.append(
                    {
                        "pet_name": pet_name,
                        "task_type": task.task_type.value,
                        "time": task.scheduled_time.strftime("%H:%M"),
                        "duration": task.duration_minutes,
                        "priority": task.priority,
                    }
                )
            st.table(schedule_rows)
        else:
            st.info("No tasks scheduled yet.")

        st.subheader("Optimized Daily Plan")
        daily_plan = st.session_state.scheduler.generate_daily_plan(
            available_minutes=st.session_state.owner.available_minutes_per_day
        )
        if daily_plan:
            daily_plan_rows = []
            for task in daily_plan:
                pet = st.session_state.owner.get_pet(task.pet_id)
                pet_name = pet.name if pet else task.pet_id
                daily_plan_rows.append(
                    {
                        "pet_name": pet_name,
                        "task_type": task.task_type.value,
                        "time": task.scheduled_time.strftime("%H:%M"),
                        "duration": task.duration_minutes,
                        "priority": task.priority,
                    }
                )
            st.table(daily_plan_rows)
        else:
            st.info("No tasks fit the current daily budget.")

        conflicts = st.session_state.scheduler.detect_conflicts()
        if conflicts:
            st.warning("Conflicts detected:")
            for first, second, conflict_type in conflicts:
                if conflict_type == "same_pet":
                    pet = st.session_state.owner.get_pet(first.pet_id)
                    pet_name = pet.name if pet else first.pet_id
                    st.warning(
                        f"⚠️ {pet_name} has overlapping tasks at {first.scheduled_time.strftime('%H:%M')}: "
                        f"{first.task_type.value} and {second.task_type.value}"
                    )
                elif conflict_type == "owner_double_booked":
                    first_pet = st.session_state.owner.get_pet(first.pet_id)
                    second_pet = st.session_state.owner.get_pet(second.pet_id)
                    first_pet_name = first_pet.name if first_pet else first.pet_id
                    second_pet_name = second_pet.name if second_pet else second.pet_id
                    st.warning(
                        f"⚠️ You're double-booked at {first.scheduled_time.strftime('%H:%M')}: "
                        f"{first.task_type.value} for {first_pet_name} and {second.task_type.value} for {second_pet_name}"
                    )

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
