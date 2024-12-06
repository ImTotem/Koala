import threading
import time

import schedule

from koala.batch.core.batch_manager import BatchManager
from koala.batch.models.work_item import WorkItem, WorkType
from koala.domain.assignment.service import AssignmentService
from koala.domain.auth.service import LoginService


class Scheduler(threading.Thread):
    def __init__(
            self,
            batch_manager: BatchManager,
            login_service: LoginService,
            assignment_service: AssignmentService
    ):
        super().__init__(daemon=False)
        # self.daemon = False
        self.batch_manager = batch_manager
        self.running: bool = False
        self.login_service = login_service
        self.assignment_service = assignment_service

        self.schedules = (
            WorkItem(
                type=WorkType.REFRESH,
                method=self.login_service.refresh,
                interval=3 * 60
            ),
            WorkItem(
                type=WorkType.COURSES,
                method=self.assignment_service.crawling_course,
                interval=5
            ),
            WorkItem(
                type=WorkType.ASSIGNMENT,
                method=self.assignment_service.crawling_assignments,
                interval=5
            ),
        )

    def run(self):
        """스케줄러 스레드 실행"""
        self.running = True

        try:
            self._execute_work(
                WorkItem(
                    type=WorkType.LOGIN,
                    method=self.login_service.login,
                    interval=0
                )
            )

            # 정기 스케줄 등록
            for work_item in self.schedules:
                self._execute_work(work_item)
                schedule.every(work_item.interval).minutes.do(
                    self._execute_work,
                    work_item
                )

            # 스케줄 실행
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            print(f"Scheduler error: {e}")

    def _execute_work(self, work_item: WorkItem):
        """작업 실행"""
        try:
            self.batch_manager.process_work(work_item)
        except Exception as e:
            print(f"Error executing {work_item.type.name}: {e}")

    def stop(self):
        """스케줄러 정지"""
        self.running = False
        schedule.clear()
