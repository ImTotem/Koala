import threading
from typing import Tuple, Set

from koala.batch.core.worker_pool import WorkerPool
from koala.batch.models.work_item import WorkItem, WorkType
from koala.domain.assignment.model import Course
from koala.utils import Observer, Subject


class BatchManager(Observer):

    def __init__(
            self,
            worker_pool: WorkerPool,
            courses: Set[Course],
    ):
        self.worker_pool = worker_pool
        self.courses = courses
        self.work_complete = threading.Event()
        self.work_complete.set()

    def process_work(self, work_item: WorkItem) -> None:
        """WorkType에 따른 WorkItem 생성 및 큐 추가"""
        self.work_complete.wait()
        self.work_complete.clear()

        work_items = self._create_works(work_item)
        self.worker_pool.extend_works(work_items)

    def _create_works(self, work_type: WorkItem) -> Tuple[WorkItem, ...]:
        if work_type.type != WorkType.ASSIGNMENT:
            return (work_type,)

        return tuple(
            WorkItem(
                type=work_type.type,
                method=work_type.method,
                interval=work_type.interval,
                arguments=(course,)
            )
            for course in self.courses
        )

    def update(self, subject: Subject) -> None:
        self.work_complete.set()
