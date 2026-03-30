import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This app helps a pet owner track pets and tasks, then generate a smart daily schedule
with sorting, filtering, recurring task support, and conflict detection.
"""
)

st.divider()

# ── Owner & Pet setup ────────────────────────────────────────────────────────

st.subheader("Owner and Pet Setup")

owner_name = st.text_input("Owner name", value=st.session_state.owner.name or "Jordan")
st.session_state.owner.name = owner_name

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Pet age", min_value=0, max_value=50, value=1)

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, species=species, age=int(age))
    st.session_state.owner.add_pet(new_pet)
    st.success(f"{pet_name} added successfully.")

if st.session_state.owner.pets:
    st.write("Registered pets:")
    for pet in st.session_state.owner.pets:
        st.write(f"- {pet.name} ({pet.species}, age {pet.age})")
else:
    st.info("No pets added yet.")

st.divider()

# ── Add a task ───────────────────────────────────────────────────────────────

st.subheader("Add a Task")

if st.session_state.owner.pets:
    pet_names = [pet.name for pet in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Choose a pet", pet_names)

    task_description = st.text_input("Task description", value="Morning walk")
    task_time = st.text_input("Task time (HH:MM, 24-hour)", value="08:00")
    task_frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add task"):
        new_task = Task(
            description=task_description,
            time=task_time,
            frequency=task_frequency,
        )
        for pet in st.session_state.owner.pets:
            if pet.name == selected_pet_name:
                pet.add_task(new_task)
                st.success(f"Task added to {pet.name}.")
                break
else:
    st.info("Add a pet first before creating tasks.")

st.divider()

# ── Current Tasks ────────────────────────────────────────────────────────────

st.subheader("Current Tasks")

filter_pet = st.selectbox(
    "Filter by pet",
    ["All pets"] + [p.name for p in st.session_state.owner.pets],
)
filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

scheduler = st.session_state.scheduler
all_tasks = scheduler.get_all_tasks()

# Apply filters
if filter_pet != "All pets":
    all_tasks = scheduler.filter_by_pet(filter_pet)

if filter_status == "Pending":
    all_tasks = [t for t in all_tasks if not t.completed]
elif filter_status == "Completed":
    all_tasks = [t for t in all_tasks if t.completed]

if all_tasks:
    task_rows = [
        {
            "Pet": t.pet_name or "—",
            "Time": t.time,
            "Description": t.description,
            "Frequency": t.frequency,
            "Status": "Done" if t.completed else "Pending",
        }
        for t in all_tasks
    ]
    st.table(task_rows)
else:
    st.info("No tasks match the current filter.")

st.divider()

# ── Smart Schedule ───────────────────────────────────────────────────────────

st.subheader("Smart Schedule")

if st.button("Generate schedule"):
    sorted_tasks = scheduler.sort_by_time()

    # Conflict warnings – shown before the schedule so the owner sees them first
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts detected.")

    if sorted_tasks:
        st.markdown("**Daily schedule (sorted by time):**")
        for task in sorted_tasks:
            status_icon = "✅" if task.completed else "🔲"
            st.write(
                f"{status_icon} **{task.time}** — {task.description} "
                f"({task.frequency}) [{task.pet_name or '—'}]"
            )
    else:
        st.warning("No tasks available to schedule.")
