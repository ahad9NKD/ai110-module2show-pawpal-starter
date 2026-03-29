from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str
    frequency: str
    completed: bool = False

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
        """Adds a new task to the pet."""
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

    def get_sorted_tasks(self) -> List[Task]:
        """Returns tasks sorted by time."""
        return sorted(self.get_all_tasks(), key=lambda task: task.time)

    def get_incomplete_tasks(self) -> List[Task]:
        """Returns only tasks that are not completed."""
        return [task for task in self.get_all_tasks() if not task.completed]