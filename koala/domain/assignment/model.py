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
            updated = False
            if (self.url != other.url or
                    self.title != other.title or
                    self.status != other.status or
                    self.start_date != other.start_date or
                    self.end_date != other.end_date
            ):
                updated = True

            self.url = other.url
            self.title = other.title
            self.status = other.status
            self.start_date = other.start_date
            self.end_date = other.end_date

            return updated

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
            if other in self.assignments:  # 과제가 존재할 경우
                return self.assignments[other.id].update(self.assignments)  # 과제 내용이 수정 되었을 경우 True, 아니면 False
            else:  # 과제가 목록에 없는 경우
                self.assignments[other.id] = other  # 과제 추가
                return True
        elif isinstance(other, defaultdict):
            updated = False
            for assignment in other.values():
                updated |= self.update(assignment)

            return updated
        elif isinstance(other, list):
            updated = False
            for assignment in other:
                updated |= self.update(assignment)

            return updated

        return False

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return hash(self) == hash(other)


__all__ = (
    'Course',
    'Status',
    'BaseAssignment',
    'VideoAssignment',
    'QuizAssignment',
    'AssignAssignment',
)
