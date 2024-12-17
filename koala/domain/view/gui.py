import tkinter as tk
from datetime import datetime

from koala.domain.assignment.service import AssignmentService
from koala.domain.auth.service import AuthService
from koala.domain.notification_manager import NotificationManager
from koala.domain.service_thread import ServiceThread
from koala.domain.view.assignment_item import AssignmentItem
from koala.domain.view.scrollable_frame import ScrollableFrame
from koala.utils import Observer, Subject


class GUI(tk.Tk, Observer):
    CRAWLING_INTERVAL = 180000  # 3분 (밀리초)
    REFRESH_INTERVAL = 10800000  # 3시간 (밀리초)

    def __init__(
            self,
            auth_service: AuthService,
            assignment_service: AssignmentService,
            notification_manager: NotificationManager
    ):
        tk.Tk.__init__(self)
        self.auth_service = auth_service
        self.assignment_service = assignment_service
        self.notification_manager = notification_manager

        self.need_update = False

        # 옵저버로 등록
        self.assignment_service.attach(self)

        self.service_thread = ServiceThread()

        self._init_gui()
        self._start_services()

        # 주기적으로 UI 업데이트가 필요한지 확인
        self._check_update()

    def update(self, subject: Subject = None):
        """업데이트 수신"""
        if isinstance(subject, AssignmentService):
            self.need_update = True

    def _init_gui(self):
        """GUI 초기화"""
        self.title("과제 및 강의 관리")
        self.geometry("800x600")

        self.frame = ScrollableFrame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)

    def _start_services(self):
        """서비스 시작"""
        self.service_thread.start()

        self.service_thread.execute(self.auth_service.login)
        self.service_thread.execute(self.assignment_service.crawling_course)

        self._start_scheduling()

    def _start_scheduling(self):
        """크롤링과 갱신 스케줄링 시작"""
        self._schedule_refresh()
        self._schedule_crawling()

    def _schedule_crawling(self):
        """크롤링 스케줄링"""
        self.service_thread.execute(self.assignment_service.crawling_assignments)
        self.after(self.CRAWLING_INTERVAL, self._schedule_crawling)

    def _schedule_refresh(self):
        """토큰 갱신 스케줄링"""
        self.service_thread.execute(self.auth_service.refresh)
        self.after(self.REFRESH_INTERVAL, self._schedule_refresh)

    def _check_update(self):
        if self.need_update:
            self._refresh_ui()
            self.notification_manager.check_new_assignments(self.assignment_service.get_assignments())
            self.need_update = False

        self.after(100, self._check_update)

    def _refresh_ui(self):
        """UI 업데이트"""
        # 기존 항목 제거
        for widget in self.frame.inner_frame.winfo_children():
            widget.destroy()

        # 새 항목 추가
        for i, assignment in enumerate(sorted(
                self.assignment_service.get_assignments(),
                key=lambda x: x.end_date or datetime.max
        )):
            item = AssignmentItem(self.frame.inner_frame, assignment, self.auth_service.get_cookies())
            item.grid(row=i, column=0, pady=5, sticky=tk.EW)

        self.frame.update_scroll_region()

    def start(self):
        """GUI 실행"""
        try:
            self.mainloop()
        finally:
            self.assignment_service.detach(self)  # 옵저버 등록 해제
            self.service_thread.stop()
            print("프로그램 종료")
