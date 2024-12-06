from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable, Tuple

from koala.domain.assignment.model import Course


class WorkType(Enum):
    LOGIN = auto()
    REFRESH = auto()
    COURSES = auto()
    ASSIGNMENT = auto()


@dataclass(kw_only=True)
class WorkItem:
    type: WorkType
    interval: int
    method: Callable
    arguments: Tuple = field(default_factory=tuple)


@dataclass
class WorkResult:
    work_type: WorkType
    success: bool
    updated: bool = False
    course: Optional[Course] = None
    error: Optional[Exception] = None
