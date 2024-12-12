import threading
from typing import Tuple, Set

from koala.batch.core.worker_pool import WorkerPool
from koala.batch.models.work_item import WorkItem, WorkType
from koala.domain.assignment.model import Course
from koala.utils import Observer, Subject


class BatchManager(Observer):
    """BatchManager 클래스는 작업을 관리하고 WorkerPool에 작업을 추가하는 역할을 합니다."""

    def __init__(
            self,
            worker_pool: WorkerPool,
            courses: Set[Course],
    ):
        """초기화 메서드로 WorkerPool과 Course 집합을 설정합니다."""
        self.worker_pool = worker_pool  # 작업을 처리할 WorkerPool 인스턴스
        self.courses = courses  # 관리할 Course 집합
        self.work_complete = threading.Event()  # 작업 완료 이벤트
        self.work_complete.set()  # 초기 상태를 '완료'로 설정

    def process_work(self, work_item: WorkItem) -> None:
        """WorkType에 따라 WorkItem을 생성하고 큐에 추가합니다."""
        self.work_complete.wait()  # 작업이 완료될 때까지 대기
        self.work_complete.clear()  # 작업이 시작되면 완료 상태를 지움

        work_items = self._create_works(work_item)  # 주어진 WorkItem에 따라 작업 생성
        self.worker_pool.extend_works(work_items)  # 생성된 작업을 WorkerPool에 추가

    def _create_works(self, work_type: WorkItem) -> Tuple[WorkItem, ...]:
        """주어진 WorkItem의 타입에 따라 작업을 생성합니다."""
        if work_type.type != WorkType.ASSIGNMENT:  # 작업 타입이 ASSIGNMENT가 아닐 경우
            return (work_type,)  # 원래의 WorkItem을 반환

        # ASSIGNMENT 타입일 경우, 각 Course에 대해 WorkItem을 생성
        return tuple(
            WorkItem(
                type=work_type.type,  # 작업 타입
                method=work_type.method,  # 작업 메서드
                interval=work_type.interval,  # 작업 간격
                arguments=(course,)  # Course를 인자로 설정
            )
            for course in self.courses  # 모든 Course에 대해 반복
        )

    def update(self, subject: Subject) -> None:
        """주어진 Subject의 상태가 변경되었을 때 호출됩니다."""
        self.work_complete.set()  # 작업 완료 상태를 설정
