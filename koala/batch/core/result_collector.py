from typing import Set

from koala.batch.models.work_item import WorkResult, WorkType
from koala.domain.assignment.model import Course
from koala.utils import Subject


class ResultCollector(Subject):

    def __init__(self, courses: Set[Course]):
        super().__init__()
        self.pending_courses: int = 0
        self.courses = courses

    def add_result(self, result: WorkResult) -> None:
        """작업 결과 추가 및 BatchManager에 알림"""
        if result.work_type != WorkType.ASSIGNMENT:
            # 일반 작업은 바로 완료 알림
            self.notify()
            return

        self.pending_courses += 1
        if self.pending_courses == len(self.courses):
            self.pending_courses = 0
            self.notify()
