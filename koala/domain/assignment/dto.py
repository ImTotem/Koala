from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from koala.domain.assignment.model import BaseAssignment, Status


@dataclass(frozen=True)
class AssignmentDTO:
    """과제 정보 DTO - 읽기 전용 데이터와 end_date 보정"""
    _id: int
    _url: str
    _title: str
    _status: Status
    _start_date: datetime
    _end_date: datetime
    _progress: Optional[int] = None  # VideoAssignment용 진행률

    @classmethod
    def factory(cls, assignment: BaseAssignment) -> 'AssignmentDTO':
        # 모델 복제
        assignment_copy = deepcopy(assignment)

        # VideoAssignment인 경우 progress 가져오기
        progress = getattr(assignment_copy, 'progress', None)

        return cls(
            _id=assignment_copy.id,
            _url=assignment_copy.url,
            _title=assignment_copy.title,
            _status=assignment_copy.status,
            _start_date=assignment_copy.start_date,
            _end_date=cls.adjust_time(assignment_copy.end_date),
            _progress=progress
        )

    @staticmethod
    def adjust_time(end_date):
        if end_date is None:
            return None

        if end_date.strftime("%H:%M:%S") == "00:00:00":
            end_date = end_date.replace(hour=23, minute=59, second=59) - timedelta(days=1)

        return end_date

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if not isinstance(other, AssignmentDTO):
            return False
        return self._id == other._id

    @property
    def progress(self) -> Optional[int]:
        return self._progress

    # 기존 properties는 동일하게 유지
    @property
    def id(self) -> int:
        return self._id

    @property
    def url(self) -> str:
        return self._url

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self):
        return self._status

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @property
    def end_date(self) -> datetime:
        return self._end_date
