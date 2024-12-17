import datetime
from collections import defaultdict
from dataclasses import field
from typing import Union, DefaultDict

from koala.domain.assignment.model import BaseAssignment
from datetime import datetime, timedelta  # 날짜 및 시간 관련 기능을 위한 datetime 모듈 임포트


# TODO : DTO 작성하기
class AssignmentDTO:
    def __init__(self, name: str, id: int, url: str, title: str, start_date: datetime, end_date: datetime, progress: int):
        self.name = name
        self.id = id
        self.url = url
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.progress = progress

    @classmethod
    def factory(cls, name, assignment: BaseAssignment):
        # TODO : 시간 A보정
        return cls(
            name=name,
            id=assignment.id,
            url=assignment.url,
            title=assignment.title,
            start_date=assignment.start_date,
            end_date=cls.adjust_time(assignment.end_date),
            progress=assignment.progress
        )

    @staticmethod
    def adjust_time(end_date: datetime):
        if end_date is None:
            return None

        if end_date.strftime("%H:%M:%S") == "00:00:00":
            end_date = end_date.replace(hour=23, minute=59, second=59) - timedelta(days=1)

        return end_date