from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional, Callable, Tuple


class WorkType(Enum):
    LOGIN = auto()
    REFRESH = auto()
    COURSES = auto()
    ASSIGNMENT = auto()


@dataclass(kw_only=True)
class WorkItem:
    type: WorkType
    priority: int
    interval: int
    method: Callable
    arguments: Tuple = field(default_factory=tuple)
    created_at: datetime = field(default_factory=datetime.now)

    def __lt__(self, other):
        """우선순위 큐를 위한 비교 연산자
        1. priority가 낮은 것이 먼저
        2. priority가 같으면 먼저 생성된 것이 먼저
        """
        if not isinstance(other, WorkItem):
            return NotImplemented
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.created_at < other.created_at


@dataclass
class WorkResult:
    work_item: WorkItem
    result: Any
    success: bool
    error: Optional[Exception] = None
    completed_at: datetime = field(default_factory=datetime.now)
