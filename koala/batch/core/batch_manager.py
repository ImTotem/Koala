import asyncio
from typing import Tuple, Set

from koala.batch.core.worker_pool import WorkerPool
from koala.batch.models.work_item import WorkItem, WorkType
from koala.domain.assignment.model import Course


class BatchManager:
    def __init__(
            self,
            worker_pool: WorkerPool,
            courses: Set[Course],
    ):
        self.worker_pool = worker_pool
        self.courses = courses

    async def process_work(self, work_item: WorkItem) -> None:
        """WorkType에 따른 WorkItem 생성 및 큐 추가"""

        work_items = self._create_works(work_item)
        self.worker_pool.extend_works(work_items)

        if self.courses:  # courses가 있으면
            assignment_works = self._create_works(work_item)
            self.worker_pool.extend_works(assignment_works)

        if work_item.type == WorkType.COURSES:
            await asyncio.sleep(1)


    def _create_works(self, work_type: WorkItem) -> Tuple[WorkItem, ...]:

        if work_type.type != WorkType.ASSIGNMENT:
            return (work_type,)

        return tuple(
            WorkItem(
                type=work_type.type,
                method=work_type.method,
                interval=work_type.interval,
                priority=work_type.priority,
                arguments=(course,)
            )
            for course in self.courses
        )
