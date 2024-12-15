import datetime

from koala.domain.assignment.model import BaseAssignment
from datetime import datetime, timedelta  # 날짜 및 시간 관련 기능을 위한 datetime 모듈 임포트


# TODO : DTO 작성하기
class AssignmentDTO:

    def __init__(self, id: int, url: str, title: str, end_date: datetime):
        self.id = id
        self.url = url
        self.title = title
        self.end_date = end_date

    @classmethod
    def factory(cls, assignment: BaseAssignment):
        # TODO : 시간 A보정
        return cls(
            id=assignment.id,
            url=assignment.url,
            title=assignment.title,
            end_date=cls.adjust_time(assignment.end_date)
        )

    @staticmethod
    def adjust_time(end_date: datetime):
        if end_date is None:
            return None

        if end_date.strftime("%H:%M:%S") == "00:00:00":
            end_date = end_date.replace(hour=23, minute=59, second=59) - timedelta(days=1)

        return end_date
