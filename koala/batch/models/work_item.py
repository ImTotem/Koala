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
    interval: int
    method: Callable
    arguments: Tuple = field(default_factory=tuple)


@dataclass
class WorkResult:
    work_type: WorkType
    success: bool
    error: Optional[Exception] = None
