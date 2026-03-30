from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str  # "HH:MM" 24-hour format for reliable string sorting
    frequency: str  # "daily", "weekly", or "once"
    completed: bool = False
    due_date: Optional[date] = None
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Marks the task as completed."""
        self.completed = True


@dataclass
class Pet:
    """Stores pet details and its care tasks."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Adds a new task to the pet and stamps it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Returns all tasks for this pet."""
        return self.tasks


@dataclass
class Owner:
    """Manages multiple pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet to the owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Returns all tasks from all of the owner's pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """Organizes and manages tasks across all pets."""

    def __init__(self, owner: Owner) -> None:
        """Initializes the scheduler with an owner."""
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Retrieves all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def sort_by_time(self) -> List[Task]:
        """Returns all tasks sorted chronologically by their HH:MM time string.

        Uses a lambda key so Python's sorted() compares times as plain strings.
        This works correctly because the HH:MM format is zero-padded, meaning
        lexicographic order equals chronological order.
        """
        return sorted(self.get_all_tasks(), key=lambda task: task.time)

    def get_sorted_tasks(self) -> List[Task]:
        """Returns tasks sorted by time (delegates to sort_by_time)."""
        return self.sort_by_time()

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Returns all tasks that belong to the named pet (case-insensitive).

        Args:
            pet_name: The name of the pet to filter on.
        """
        return [
            task for task in self.get_all_tasks()
            if task.pet_name.lower() == pet_name.lower()
        ]

    def filter_by_status(self, completed: bool) -> List[Task]:
        """Returns tasks filtered by completion status.

        Args:
            completed: Pass True to get finished tasks, False for pending ones.
        """
        return [task for task in self.get_all_tasks() if task.completed == completed]

    def get_incomplete_tasks(self) -> List[Task]:
        """Returns only tasks that are not completed."""
        return self.filter_by_status(completed=False)

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Marks a task complete and schedules the next occurrence for recurring tasks.

        For "daily" tasks the next due date is today + 1 day.
        For "weekly" tasks the next due date is today + 7 days.
        "once" tasks are simply marked complete with no follow-up created.

        Args:
            task: The task to complete.

        Returns:
            The newly created follow-up Task, or None for one-time tasks.
        """
        task.mark_complete()

        frequency = task.frequency.lower()
        if frequency == "daily":
            delta = timedelta(days=1)
        elif frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None

        base_date = task.due_date if task.due_date is not None else date.today()
        next_task = Task(
            description=task.description,
            time=task.time,
            frequency=task.frequency,
            due_date=base_date + delta,
            pet_name=task.pet_name,
        )

        for pet in self.owner.pets:
            if pet.name == task.pet_name:
                pet.tasks.append(next_task)
                break

        return next_task

    def detect_conflicts(self) -> List[str]:
        """Returns warning messages for any tasks sharing the same time slot.

        Only checks for exact time-string matches (e.g., two tasks both at
        "09:00"). It does not model task durations, so overlapping-but-not-
        identical windows are not flagged — see reflection.md 2b for the
        tradeoff discussion.

        Returns:
            A list of human-readable conflict strings, empty if none exist.
        """
        time_map: dict = defaultdict(list)
        for task in self.get_all_tasks():
            if not task.completed:
                time_map[task.time].append(task)

        warnings = []
        for time_slot, tasks in time_map.items():
            if len(tasks) > 1:
                details = ", ".join(
                    f"'{t.description}' ({t.pet_name or 'unassigned'})"
                    for t in tasks
                )
                warnings.append(f"⚠ Conflict at {time_slot}: {details}")

        return warnings
