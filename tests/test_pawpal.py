"""
Automated test suite for PawPal+ core scheduling logic.

Coverage:
  - Task completion state
  - Pet task registration and pet_name stamping
  - Scheduler sorting correctness (chronological order)
  - filter_by_pet (happy path + case-insensitivity + unknown pet)
  - filter_by_status / get_incomplete_tasks
  - Recurring task auto-creation (daily → +1 day, weekly → +7 days, once → None)
  - Conflict detection (same-time flagged, different times clean, completed tasks ignored)
  - Edge cases: owner with no pets, pet with no tasks
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_scheduler(*pets):
    """Create a minimal Owner + Scheduler pre-loaded with the given pets."""
    owner = Owner(name="Test Owner")
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


def make_pet(name="Rex", tasks=None):
    """Create a Pet and optionally attach a list of Tasks to it."""
    pet = Pet(name=name, species="Dog", age=2)
    for task in (tasks or []):
        pet.add_task(task)
    return pet


# ---------------------------------------------------------------------------
# Existing baseline tests (kept and extended)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task(description="Feed pet", time="09:00", frequency="daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = make_pet()
    task = Task(description="Walk dog", time="08:00", frequency="daily")
    initial_count = len(pet.tasks)
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1


def test_add_task_stamps_pet_name():
    """add_task should write the pet's name onto the task."""
    pet = make_pet(name="Bella")
    task = Task(description="Groom", time="10:00", frequency="weekly")
    pet.add_task(task)
    assert task.pet_name == "Bella"


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """Tasks added out of order should come back in HH:MM order."""
    pet = make_pet(tasks=[
        Task(description="Evening meds", time="20:00", frequency="daily"),
        Task(description="Morning walk", time="07:00", frequency="daily"),
        Task(description="Lunch feed",   time="12:30", frequency="daily"),
    ])
    scheduler = make_scheduler(pet)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for t in sorted_tasks]
    assert times == sorted(times), f"Expected sorted times but got {times}"


def test_sort_by_time_single_task():
    """A single task should be returned unchanged."""
    pet = make_pet(tasks=[Task(description="Only task", time="09:00", frequency="once")])
    scheduler = make_scheduler(pet)
    assert len(scheduler.sort_by_time()) == 1


def test_sort_by_time_no_tasks():
    """A scheduler with no tasks should return an empty list without error."""
    scheduler = make_scheduler(make_pet())
    assert scheduler.sort_by_time() == []


def test_sort_preserves_all_tasks():
    """Sorting should not drop or duplicate any tasks."""
    tasks = [
        Task(description="A", time="15:00", frequency="daily"),
        Task(description="B", time="06:00", frequency="daily"),
        Task(description="C", time="11:00", frequency="daily"),
    ]
    pet = make_pet(tasks=tasks)
    scheduler = make_scheduler(pet)
    assert len(scheduler.sort_by_time()) == 3


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------

def test_filter_by_pet_returns_only_that_pets_tasks():
    rocky = make_pet("Rocky", [Task(description="Walk",  time="08:00", frequency="daily")])
    milo  = make_pet("Milo",  [Task(description="Meds",  time="09:00", frequency="daily")])
    scheduler = make_scheduler(rocky, milo)

    rocky_tasks = scheduler.filter_by_pet("Rocky")
    assert all(t.pet_name == "Rocky" for t in rocky_tasks)
    assert len(rocky_tasks) == 1


def test_filter_by_pet_case_insensitive():
    pet = make_pet("Bella", [Task(description="Groom", time="10:00", frequency="weekly")])
    scheduler = make_scheduler(pet)
    assert len(scheduler.filter_by_pet("bella")) == 1
    assert len(scheduler.filter_by_pet("BELLA")) == 1


def test_filter_by_pet_unknown_name_returns_empty():
    pet = make_pet("Rocky", [Task(description="Walk", time="08:00", frequency="daily")])
    scheduler = make_scheduler(pet)
    assert scheduler.filter_by_pet("NoSuchPet") == []


def test_filter_by_status_pending():
    pet = make_pet(tasks=[
        Task(description="Done task",    time="07:00", frequency="once", completed=True),
        Task(description="Pending task", time="08:00", frequency="daily"),
    ])
    scheduler = make_scheduler(pet)
    pending = scheduler.filter_by_status(completed=False)
    assert len(pending) == 1
    assert pending[0].description == "Pending task"


def test_filter_by_status_completed():
    pet = make_pet(tasks=[
        Task(description="Done task",    time="07:00", frequency="once", completed=True),
        Task(description="Pending task", time="08:00", frequency="daily"),
    ])
    scheduler = make_scheduler(pet)
    done = scheduler.filter_by_status(completed=True)
    assert len(done) == 1
    assert done[0].description == "Done task"


def test_get_incomplete_tasks_excludes_completed():
    pet = make_pet(tasks=[
        Task(description="Done",    time="07:00", frequency="once", completed=True),
        Task(description="Pending", time="08:00", frequency="daily"),
    ])
    scheduler = make_scheduler(pet)
    assert len(scheduler.get_incomplete_tasks()) == 1


# ---------------------------------------------------------------------------
# Recurring task tests
# ---------------------------------------------------------------------------

def test_daily_task_creates_next_day_occurrence():
    """Completing a daily task should add a new task due tomorrow."""
    today = date(2026, 3, 29)
    task = Task(description="Morning walk", time="08:00", frequency="daily", due_date=today)
    pet = make_pet("Rocky", [task])
    scheduler = make_scheduler(pet)

    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.description == "Morning walk"
    assert next_task.completed is False


def test_weekly_task_creates_next_week_occurrence():
    """Completing a weekly task should add a new task due in 7 days."""
    today = date(2026, 3, 29)
    task = Task(description="Grooming", time="14:00", frequency="weekly", due_date=today)
    pet = make_pet("Milo", [task])
    scheduler = make_scheduler(pet)

    next_task = scheduler.mark_task_complete(task)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_once_task_returns_none():
    """Completing a one-time task should NOT create a follow-up."""
    task = Task(description="Vet visit", time="10:00", frequency="once", due_date=date.today())
    pet = make_pet("Rocky", [task])
    scheduler = make_scheduler(pet)

    result = scheduler.mark_task_complete(task)
    assert result is None


def test_recurring_task_appended_to_correct_pet():
    """The new recurrence should appear in the original pet's task list."""
    today = date(2026, 3, 29)
    task = Task(description="Feed", time="08:00", frequency="daily", due_date=today)
    rocky = make_pet("Rocky", [task])
    milo  = make_pet("Milo")
    scheduler = make_scheduler(rocky, milo)

    scheduler.mark_task_complete(task)

    assert len(rocky.tasks) == 2   # original + new
    assert len(milo.tasks) == 0    # unchanged


def test_mark_task_complete_marks_original_done():
    """mark_task_complete should also flip the original task to completed."""
    task = Task(description="Walk", time="08:00", frequency="daily", due_date=date.today())
    pet = make_pet("Rocky", [task])
    scheduler = make_scheduler(pet)

    scheduler.mark_task_complete(task)
    assert task.completed is True


def test_recurring_task_inherits_time_and_frequency():
    today = date(2026, 3, 29)
    task = Task(description="Meds", time="07:30", frequency="daily", due_date=today)
    pet = make_pet("Milo", [task])
    scheduler = make_scheduler(pet)

    next_task = scheduler.mark_task_complete(task)
    assert next_task.time == "07:30"
    assert next_task.frequency == "daily"


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_same_time():
    """Two incomplete tasks at the same time should produce a conflict warning."""
    pet = make_pet(tasks=[
        Task(description="Walk",   time="09:00", frequency="daily"),
        Task(description="Vet",    time="09:00", frequency="once"),
    ])
    scheduler = make_scheduler(pet)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "09:00" in warnings[0]


def test_detect_conflicts_no_conflicts():
    """Tasks at different times should return an empty list."""
    pet = make_pet(tasks=[
        Task(description="Walk",  time="08:00", frequency="daily"),
        Task(description="Feed",  time="09:00", frequency="daily"),
        Task(description="Meds",  time="20:00", frequency="daily"),
    ])
    scheduler = make_scheduler(pet)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_ignores_completed_tasks():
    """A completed task should not be counted in conflict detection."""
    pet = make_pet(tasks=[
        Task(description="Done walk",    time="09:00", frequency="daily", completed=True),
        Task(description="Pending feed", time="09:00", frequency="daily"),
    ])
    scheduler = make_scheduler(pet)
    # Only one incomplete task at 09:00 → no conflict
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_multiple_slots():
    """Multiple independent conflict slots should each produce a warning."""
    pet = make_pet(tasks=[
        Task(description="A", time="08:00", frequency="daily"),
        Task(description="B", time="08:00", frequency="daily"),
        Task(description="C", time="14:00", frequency="daily"),
        Task(description="D", time="14:00", frequency="daily"),
    ])
    scheduler = make_scheduler(pet)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 2


def test_detect_conflicts_across_multiple_pets():
    """Conflicts between tasks belonging to different pets are still flagged."""
    rocky = make_pet("Rocky", [Task(description="Walk",     time="09:00", frequency="daily")])
    milo  = make_pet("Milo",  [Task(description="Playtime", time="09:00", frequency="daily")])
    scheduler = make_scheduler(rocky, milo)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "Rocky" in warnings[0] or "Milo" in warnings[0]


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

def test_owner_with_no_pets_returns_empty_schedule():
    scheduler = make_scheduler()
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.get_incomplete_tasks() == []


def test_pet_with_no_tasks_does_not_affect_schedule():
    empty_pet = make_pet("Ghost")
    busy_pet  = make_pet("Buddy", [Task(description="Walk", time="08:00", frequency="daily")])
    scheduler = make_scheduler(empty_pet, busy_pet)
    assert len(scheduler.sort_by_time()) == 1
