from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(tasks):
    print("\n=== Today's Schedule ===")
    if not tasks:
        print("No tasks scheduled for today.")
        return

    for i, task in enumerate(tasks, start=1):
        status = "Done" if task.completed else "Pending"
        print(f"{i}. {task.time} | {task.description} | {task.frequency} | {status}")


def main():
    # Create owner
    owner = Owner(name="Abdoul")

    # Create pets
    dog = Pet(name="Rocky", species="Dog", age=3)
    cat = Pet(name="Milo", species="Cat", age=2)

    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Create tasks
    task1 = Task(description="Morning walk", time="08:00", frequency="Daily")
    task2 = Task(description="Feed Rocky", time="09:00", frequency="Daily")
    task3 = Task(description="Give Milo medicine", time="07:30", frequency="Daily")

    # Add tasks to pets
    dog.add_task(task1)
    dog.add_task(task2)
    cat.add_task(task3)

    # Create scheduler
    scheduler = Scheduler(owner)

    # Print sorted schedule
    today_tasks = scheduler.get_sorted_tasks()
    print_schedule(today_tasks)


if __name__ == "__main__":
    main()