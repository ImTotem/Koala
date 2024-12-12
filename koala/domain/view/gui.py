import tkinter as tk
import webbrowser
from datetime import datetime
from multiprocessing import Queue
from queue import Empty
from tkinter import ttk

from dependency_injector.wiring import inject

from koala.domain.assignment.model import Course, BaseAssignment, VideoAssignment


class GUI(tk.Tk):

    def __init__(self, queue: Queue):
        super().__init__()

        self.queue = queue
        self.current_assignments = {}

        self.title("과제 및 강의 관리")
        self.geometry("800x600")

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.inner_frame.columnconfigure(0, weight=1)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW,
                                                       width=self.canvas.winfo_width())

        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

        self.after(100, self.check_update)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._update_scroll_region()

    def _update_scroll_region(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def check_update(self) -> None:
        try:
            while True:
                course = self.queue.get_nowait()
                self.update_ui(course)
                self._update_scroll_region()
        except Empty:
            pass
        finally:
            self.after(100, self.check_update)

    def start(self):
        try:
            self.mainloop()
        finally:
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
            for widget in self.inner_frame.winfo_children():
                widget.destroy()

            for i, assignment in enumerate(sorted(new_assignments.values(), key=lambda x: x.end_date or datetime.max)):
                self._create_assignment_frame(i, assignment)

        self.current_assignments = new_assignments
        self._update_scroll_region()

    def _is_assignment_changed(self, old: BaseAssignment, new: BaseAssignment) -> bool:
        return (old.url != new.url or
                old.title != new.title or
                old.status != new.status or
                old.start_date != new.start_date or
                old.end_date != new.end_date)

    def _create_assignment_frame(self, index: int, assignment: BaseAssignment) -> None:
        task_frame = ttk.Frame(self.inner_frame, padding=10)
        task_frame.grid(row=index, column=0, pady=5, sticky=tk.EW)

        # Configure columns
        task_frame.columnconfigure(0, weight=1)  # Title column - expandable
        task_frame.columnconfigure(1, minsize=300)  # Fixed width for right side elements

        def make_url_opener(url):
            return lambda: webbrowser.open(url)

        date_str = f"{assignment.start_date.strftime('%Y-%m-%d')} ~ {assignment.end_date.strftime('%Y-%m-%d')}" if assignment.start_date and assignment.end_date else "날짜 미정"

        dday = ""
        if assignment.end_date:
            days_left = (assignment.end_date.date() - datetime.now().date()).days
            if days_left > 0:
                dday = f"D-{days_left}"
            elif days_left == 0:
                dday = "D-Day"
            else:
                dday = f"D+{abs(days_left)}"

        detail = f"상태: {assignment.status.value if assignment.status else '상태 미정'}"
        if isinstance(assignment, VideoAssignment):
            detail += f" | 진행률: {assignment.progress}%"

        # Left side (title and date)
        left_frame = ttk.Frame(task_frame)
        left_frame.grid(row=0, column=0, sticky=tk.EW, padx=10)

        title_label = ttk.Label(left_frame, text=assignment.title, font=("Arial", 30))
        title_label.pack(anchor=tk.W)

        # Add tooltip
        self._create_tooltip(title_label, assignment.title)

        ttk.Label(left_frame, text=date_str, font=("Arial", 15, "italic")).pack(anchor=tk.W)

        # Right side container
        right_frame = ttk.Frame(task_frame)
        right_frame.grid(row=0, column=1, sticky=tk.E)

        # Status
        status_label = ttk.Label(right_frame, text=detail, font=("Arial", 15))
        status_label.pack(side=tk.LEFT, padx=(0, 10))

        # D-day
        dday_label = ttk.Label(right_frame, text=dday, font=("Arial", 20, "bold"))
        dday_label.pack(side=tk.LEFT, padx=(0, 10))

        # Classroom button
        classroom_btn = ttk.Button(right_frame, text="강의실", width=6,
                                   command=make_url_opener(assignment.url))
        classroom_btn.pack(side=tk.LEFT, padx=(0, 10))

    def _create_tooltip(self, widget, text):
        """마우스 호버 시 전체 텍스트를 보여주는 툴팁 생성"""
        tooltip = tk.Toplevel(self)
        tooltip.withdraw()
        tooltip.overrideredirect(True)

        label = ttk.Label(tooltip, text=text, padding=5)
        label.pack()

        def show_tooltip(event):
            tooltip.deiconify()
            x = widget.winfo_rootx() + widget.winfo_width() // 2
            y = widget.winfo_rooty() + widget.winfo_height()
            tooltip.geometry(f"+{x}+{y}")

        def hide_tooltip(event):
            tooltip.withdraw()

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)


@inject
def gui_main(
        queue: Queue
):
    gui = GUI(queue)
    gui.start()
