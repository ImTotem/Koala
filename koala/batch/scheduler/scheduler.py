import asyncio
import threading
import time
from typing import Optional

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
        super().__init__()
        self.daemon = True
        self.batch_manager = batch_manager
        self.running: bool = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.login_service = login_service
        self.assignment_service = assignment_service

        self.schedules = (
            WorkItem(
                type=WorkType.REFRESH,
                method=self.login_service.refresh,
                interval=3 * 60,
                priority=1
            ),
            WorkItem(
                type=WorkType.COURSES,
                method=self.assignment_service.crawling_course,
                interval=5,
                priority=2
            ),
            WorkItem(
                type=WorkType.ASSIGNMENT,
                method=self.assignment_service.crawling_assignments,
                interval=5,
                priority=3
            ),
        )

    def run(self):
        """스케줄러 스레드 실행"""
        self.running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            # 초기 작업 순차 실행
            self._execute_initial_tasks()

            # 정기 스케줄 등록
            for work_item in self.schedules:
                schedule.every(work_item.interval).minutes.do(self._execute_work, work_item)

            # 스케줄 실행
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        finally:
            if not self.loop.is_closed():
                self.loop.close()

    def _execute_initial_tasks(self):
        """프로그램 시작시 초기 작업 순차 실행"""
        initial_works = (
            WorkItem(
                type=WorkType.LOGIN,
                method=self.login_service.login,
                interval=0,
                priority=0
            ),
            *self.schedules
        )

        try:
            for work_item in initial_works:
                self._execute_work(work_item)
        except Exception as e:
            print(f"Error during initial tasks: {e}")
            raise

    def _execute_work(self, work_item: WorkItem):
        """작업 실행 (대기하지 않음)"""
        try:
            # BatchManager에 작업 전달
            self.loop.run_until_complete(self.batch_manager.process_work(work_item))
            # asyncio.run_coroutine_threadsafe(
            #     self.batch_manager.process_work(work_item),
            #     self.loop
            # )
        except Exception as e:
            print(f"Error executing {work_item.type.name}: {e}")

    def stop(self):
        """스케줄러 정지"""
        self.running = False
        schedule.clear()
