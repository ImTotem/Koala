from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import DefaultDict, Union

class Status(Enum):
    오픈전 = '오픈전'
    진행중 = '진행중'
    완료 = '종료'
    지각 = '지각'
    미제출 = '미제출'
    비활성 = '비활성'
    활성 = '활성'
    기한경과 = '기한경과'

    @classmethod
    def from_string(cls, value: str) -> 'Status':
        try:
            return cls(value)
        except ValueError:
            try:
                return cls.__members__[value.upper()]
            except KeyError:
                raise ValueError(f"'{value}' is not a valid {cls.__name__}")

@dataclass
class BaseAssignment:
    _id: int
    url: str
    title: str
    status: Union[Status, None]
    start_date: Union[datetime, None]
    end_date: Union[datetime, None]

    @property
    def id(self):
        return self._id

    def update(self, other):
        if isinstance(other, BaseAssignment):
            self.url = other.url
            self.title = other.title
            self.status = other.status
            self.start_date = other.start_date
            self.end_date = other.end_date

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other: object):
        return hash(self) == hash(other)

@dataclass(eq=False)
class VideoAssignment(BaseAssignment):
    progress: int

QuizAssignment = BaseAssignment
AssignAssignment = BaseAssignment

@dataclass
class Course:
    _id: int
    url: str
    name: str
    assignments: DefaultDict[int, BaseAssignment] = field(default_factory=lambda: defaultdict(BaseAssignment))

    @property
    def id(self):
        return self._id

    def update(self, other):
        if isinstance(other, BaseAssignment):
            if other in self.assignments:
                self.assignments[other.id].update(other)
            else:
                self.assignments[other.id] = other
        elif isinstance(other, defaultdict):
            for assignment in other.values():
                self.update(assignment)
        elif isinstance(other, list):
            for assignment in other:
                self.update(assignment)

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return hash(self) == hash(other)
