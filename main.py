from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(tasks, label="Schedule"):
    print(f"\n=== {label} ===")
    if not tasks:
        print("  (none)")
        return
    for i, task in enumerate(tasks, start=1):
        status = "Done" if task.completed else "Pending"
        due = f" | due {task.due_date}" if task.due_date else ""
        print(f"  {i}. {task.time} | {task.description} | {task.frequency} | {status}{due} [{task.pet_name}]")


def main():
    # --- Setup ---
    owner = Owner(name="Abdoul")
    dog = Pet(name="Rocky", species="Dog", age=3)
    cat = Pet(name="Milo", species="Cat", age=2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Tasks added intentionally out of chronological order
    dog.add_task(Task(description="Evening walk",    time="18:00", frequency="daily",  due_date=date.today()))
    dog.add_task(Task(description="Morning walk",    time="08:00", frequency="daily",  due_date=date.today()))
    dog.add_task(Task(description="Feed Rocky",      time="09:00", frequency="daily",  due_date=date.today()))
    cat.add_task(Task(description="Give Milo meds",  time="07:30", frequency="daily",  due_date=date.today()))
    cat.add_task(Task(description="Grooming",        time="14:00", frequency="weekly", due_date=date.today()))

    # Conflict: Rocky's vet visit and Milo's playtime both at 09:00
    dog.add_task(Task(description="Vet check-up",    time="09:00", frequency="once"))
    cat.add_task(Task(description="Playtime",        time="14:00", frequency="daily",  due_date=date.today()))

    scheduler = Scheduler(owner)

    # --- Sorting ---
    print_schedule(scheduler.sort_by_time(), label="All Tasks Sorted by Time")

    # --- Filtering by pet ---
    print_schedule(scheduler.filter_by_pet("Rocky"), label="Rocky's Tasks")
    print_schedule(scheduler.filter_by_pet("Milo"),  label="Milo's Tasks")

    # --- Filtering by status ---
    print_schedule(scheduler.filter_by_status(completed=False), label="Pending Tasks")

    # --- Recurring task auto-scheduling ---
    print("\n=== Recurring Task Demo ===")
    morning_walk = dog.tasks[1]  # "Morning walk" at 08:00
    print(f"  Completing: '{morning_walk.description}' (due {morning_walk.due_date})")
    next_task = scheduler.mark_task_complete(morning_walk)
    if next_task:
        print(f"  Auto-scheduled next: '{next_task.description}' due {next_task.due_date}")

    # --- Conflict detection ---
    print("\n=== Conflict Detection ===")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")

    # --- Final sorted view (post-completion) ---
    print_schedule(scheduler.sort_by_time(), label="Final Schedule (after completion)")


if __name__ == "__main__":
    main()
