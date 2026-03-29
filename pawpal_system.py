from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: Dict[str, str] = field(default_factory=dict)

    def update_preferences(self, new_preferences: Dict[str, str]) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner_name: str

    def get_profile(self) -> str:
        pass


@dataclass
class Task:
    title: str
    category: str
    duration: int
    priority: int
    required: bool = False
    preferred_time: Optional[str] = None
    completed: bool = False

    def mark_completed(self) -> None:
        pass

    def update_priority(self, new_priority: int) -> None:
        pass


@dataclass
class DailyPlan:
    selected_tasks: List[Task] = field(default_factory=list)
    total_minutes: int = 0
    reasoning: List[str] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass


class SchedulePlanner:
    def __init__(self) -> None:
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, task_index: int, updated_task: Task) -> None:
        pass

    def remove_task(self, task_index: int) -> None:
        pass

    def rank_tasks(self) -> List[Task]:
        pass

    def generate_daily_plan(self, owner: Owner) -> DailyPlan:
        pass

    def explain_plan(self, plan: DailyPlan) -> List[str]:
        pass