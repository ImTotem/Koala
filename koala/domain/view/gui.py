import tkinter as tk
from tkinter import ttk
import webbrowser

from math import ceil

from dependency_injector.wiring import inject, Provide

from koala.di import DI
from koala.domain.assignment.controller import AssignmentController
from koala.utils import Observer, Subject

class GUI(tk.Tk, Observer):

    def __init__(self, controller: AssignmentController):
        super().__init__()

        self._controller = controller

        # 윈도우 설정
        self.title("과제 및 강의 관리")
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas 생성
        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 스크롤 바 생성 및 Canvas에 연결
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Canvas 내부에 Frame 생성
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

        # Canvas의 스크롤 영역 설정
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Canvas 크기 조정 함수
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", on_frame_configure)

        def on_mouse_wheel(event):
            """마우스 휠로 스크롤을 처리하는 함수"""
            delta = ceil(event.delta / 120)
            if event.delta < 0:
                delta = (event.delta // 120)
            canvas.yview_scroll(-1 * delta, "units")  # Windows/Mac

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Windows/Mac

    def start(self):
        self.mainloop()

    def update(self, subject: Subject) -> None:
        self.update_ui()

    def update_ui(self) -> None:
        print(self._controller.get_assignments())


@inject
def gui_main(controller: AssignmentController = Provide[DI.assignment.controller]):
    gui = GUI(controller)
    controller.attach(gui)
    gui.start()

# for i, task_data in enumerate(tasks):
#     # 각 과제 항목을 독립적으로 추가
#     task_frame = ttk.Frame(inner_frame, padding=10, relief=tk.SOLID)
#     task_frame.grid(row=i, column=0, pady=5, sticky=tk.EW)
#
#     open_url = lambda : webbrowser.open(task_data["web"])
#
#     ttk.Label(task_frame, text=task_data["title"], font=("Arial", 30)).grid(row=0, column=0, sticky="w")
#     ttk.Label(task_frame, text=task_data["date"], font=("Arial", 15, "italic")).grid(row=1, column=0, sticky="w")
#     ttk.Label(task_frame, text=task_data["detail"], font=("Arial", 15)).grid(row=0, column=1, rowspan=2, sticky="w", padx=(20,150))
#     ttk.Label(task_frame, text=task_data["dday"], font=("Arial", 20, "bold")).grid(row=0, column=2, rowspan=2, sticky="e", padx=10)
#     ttk.Button(task_frame, text="강의실", width=6, command=open_url).grid(row=0, column=3, rowspan=2, sticky="e", padx=10)
