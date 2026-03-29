from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(
        description="Feed pet",
        time="09:00",
        frequency="Daily"
    )

    # Before
    assert task.completed is False

    # Action
    task.mark_complete()

    # After
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Rocky", species="Dog", age=3)

    task = Task(
        description="Walk dog",
        time="08:00",
        frequency="Daily"
    )

    initial_count = len(pet.tasks)

    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1