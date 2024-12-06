import tkinter as tk
import webbrowser
from datetime import datetime
from math import ceil
from multiprocessing import Queue
from queue import Empty
from tkinter import ttk

from dependency_injector.wiring import inject

from koala.domain.assignment.model import Course, BaseAssignment, VideoAssignment


class GUI(tk.Tk):

    def __init__(self, queue: Queue):
        super().__init__()

        self.queue = queue
        self.current_assignments = {}  # 현재 표시된 assignments 저장

        # 윈도우 설정
        self.title("과제 및 강의 관리")
        self.geometry("800x600")
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas 생성
        self.canvas = tk.Canvas(main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 스크롤 바 생성 및 Canvas에 연결
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Canvas 내부에 Frame 생성
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW)

        self.after(100, self.check_update)

    def _attach_scroll(self):
        # Canvas의 스크롤 영역 설정
        self.inner_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Canvas 크기 조정 함수
        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.inner_frame.bind("<Configure>", on_frame_configure)

        def on_mouse_wheel(event):
            """마우스 휠로 스크롤을 처리하는 함수"""
            delta = ceil(event.delta / 120)
            if event.delta < 0:
                delta = (event.delta // 120)
            self.canvas.yview_scroll(-1 * delta, "units")  # Windows/Mac

        self.canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/Mac

    def check_update(self) -> None:
        try:
            # 큐에서 업데이트 확인 (non-blocking)
            while True:
                course = self.queue.get_nowait()
                self.update_ui(course)
                self._attach_scroll()
        except Empty:
            pass
        finally:
            self.after(100, self.check_update)

    def start(self):
        try:
            self.mainloop()
        finally:
            # GUI 종료시 정리
            print("GUI closing...")

    def update_ui(self, course: Course) -> None:
        updated = False
        new_assignments = {}

        for assignment in course.assignments.values():
            new_assignments[assignment.id] = assignment
            if (assignment.id not in self.current_assignments or
                    self._is_assignment_changed(self.current_assignments[assignment.id], assignment)):
                updated = True

        if updated:
            # 기존 프레임들 제거
            for widget in self.inner_frame.winfo_children():
                widget.destroy()

            # 새로운 데이터로 프레임 다시 그리기
            for i, assignment in enumerate(sorted(new_assignments.values(), key=lambda x: x.end_date or datetime.max)):
                self._create_assignment_frame(i, assignment)

        self.current_assignments = new_assignments
        self._attach_scroll()

    def _is_assignment_changed(self, old: BaseAssignment, new: BaseAssignment) -> bool:
        return (old.url != new.url or
                old.title != new.title or
                old.status != new.status or
                old.start_date != new.start_date or
                old.end_date != new.end_date)

    def _create_assignment_frame(self, index: int, assignment: BaseAssignment) -> None:
        task_frame = ttk.Frame(self.inner_frame, padding=10, relief=tk.SOLID)
        task_frame.grid(row=index, column=0, pady=5, sticky=tk.EW)

        # url을 위한 클로저 함수
        def make_url_opener(url):
            return lambda: webbrowser.open(url)

        # 날짜 포맷팅
        date_str = f"{assignment.start_date.strftime('%Y-%m-%d')} ~ {assignment.end_date.strftime('%Y-%m-%d')}" if assignment.start_date and assignment.end_date else "날짜 미정"

        # D-day 계산
        dday = ""
        if assignment.end_date:
            days_left = (assignment.end_date.date() - datetime.now().date()).days
            dday = f"D{days_left}" if days_left <= 0 else f"D+{abs(days_left)}"

        # 상태에 따른 세부 정보
        detail = f"상태: {assignment.status.value if assignment.status else '상태 미정'}"
        if isinstance(assignment, VideoAssignment):
            detail += f" | 진행률: {assignment.progress}%"

        # UI 컴포넌트 생성
        ttk.Label(task_frame, text=assignment.title, font=("Arial", 30)).grid(row=0, column=0, sticky="w")
        ttk.Label(task_frame, text=date_str, font=("Arial", 15, "italic")).grid(row=1, column=0, sticky="w")
        ttk.Label(task_frame, text=detail, font=("Arial", 15)).grid(row=0, column=1, rowspan=2, sticky="w",
                                                                    padx=(20, 150))
        ttk.Label(task_frame, text=dday, font=("Arial", 20, "bold")).grid(row=0, column=2, rowspan=2, sticky="e",
                                                                          padx=10)
        ttk.Button(task_frame, text="강의실", width=6, command=make_url_opener(assignment.url)).grid(row=0, column=3,
                                                                                                  rowspan=2, sticky="e",
                                                                                                  padx=10)


@inject
def gui_main(
        queue: Queue
):
    gui = GUI(queue)

    gui.start()
