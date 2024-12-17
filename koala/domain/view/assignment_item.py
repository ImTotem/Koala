import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import ttk

from requests.cookies import RequestsCookieJar

from koala.domain.assignment.model import BaseAssignment, VideoAssignment


class AssignmentItem(ttk.Frame):
    def __init__(
            self,
            parent,
            assignment: BaseAssignment,
            cookies: RequestsCookieJar
    ):
        super().__init__(parent, padding=10)
        self.assignment = assignment
        self.cookies = cookies
        self._create_widgets()

    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, minsize=300)

        left_frame = self._create_info_frame()
        right_frame = self._create_status_frame()

        left_frame.grid(row=0, column=0, sticky=tk.EW, padx=10)
        right_frame.grid(row=0, column=1, sticky=tk.E)

    def _create_info_frame(self):
        frame = ttk.Frame(self)

        ttk.Label(frame, text=self.assignment.title,
                  font=("Arial", 30)).pack(anchor=tk.W)

        date_str = self._format_date()
        ttk.Label(frame, text=date_str,
                  font=("Arial", 15, "italic")).pack(anchor=tk.W)

        return frame

    def _create_status_frame(self):
        frame = ttk.Frame(self)

        ttk.Label(frame, text=self._get_status_text(),
                  font=("Arial", 15)).pack(side=tk.LEFT, padx=(0, 10))

        if (dday := self._calculate_dday()):
            ttk.Label(frame, text=dday,
                      font=("Arial", 20, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(frame, text="강의실", width=6,
                   command=self._open_classroom).pack(side=tk.LEFT, padx=(0, 10))

        return frame

    def _format_date(self):
        if self.assignment.start_date and self.assignment.end_date:
            return f"{self.assignment.start_date:%Y-%m-%d} ~ {self.assignment.end_date:%Y-%m-%d}"
        return "날짜 미정"

    def _get_status_text(self):
        status = f"상태: {self.assignment.status.value if self.assignment.status else '상태 미정'}"
        if isinstance(self.assignment, VideoAssignment):
            status += f" | 진행률: {self.assignment.progress}%"
        return status

    def _calculate_dday(self):
        if not self.assignment.end_date:
            return ""

        days_left = (self.assignment.end_date.date() - datetime.now().date()).days
        if days_left > 0:
            return f"D-{days_left}"
        elif days_left == 0:
            return "D-Day"
        return f"D+{abs(days_left)}"

    def _open_classroom(self):
        webbrowser.open(self.assignment.url)
