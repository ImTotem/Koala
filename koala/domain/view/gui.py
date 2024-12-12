import tkinter as tk  # tkinter 모듈을 tk라는 이름으로 임포트 (GUI 생성용)
import webbrowser  # 웹 브라우저를 열기 위한 모듈 임포트
from datetime import datetime  # 날짜 및 시간 관련 기능을 위한 datetime 모듈 임포트
from multiprocessing import Queue  # 멀티프로세싱을 위한 Queue 클래스 임포트
from queue import Empty  # 큐가 비어있을 때 발생하는 예외 클래스 임포트
from tkinter import ttk  # tkinter의 테마화된 위젯을 사용하기 위한 ttk 모듈 임포트

from dependency_injector.wiring import inject  # 의존성 주입을 위한 inject 데코레이터 임포트

from koala.domain.assignment.model import Course, BaseAssignment, VideoAssignment  # 과제 관련 모델 클래스 임포트


class GUI(tk.Tk):  # tkinter의 Tk 클래스를 상속받아 GUI 클래스 정의
    def __init__(self, queue: Queue):  # 생성자, 큐를 인자로 받음
        super().__init__()  # 부모 클래스의 생성자 호출

        self.queue = queue  # 큐를 인스턴스 변수에 저장
        self.current_assignments = {}  # 현재 과제를 저장할 딕셔너리 초기화

        self.title("과제 및 강의 관리")  # 윈도우 제목 설정
        self.geometry("800x600")  # 윈도우 크기 설정

        main_frame = ttk.Frame(self, padding=20)  # 메인 프레임 생성
        main_frame.pack(fill=tk.BOTH, expand=True)  # 프레임을 채우고 확장하도록 설정
        main_frame.columnconfigure(0, weight=1)  # 첫 번째 열의 가중치 설정

        self.canvas = tk.Canvas(main_frame)  # 캔버스 생성
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)  # 세로 스크롤바 생성

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # 캔버스를 왼쪽에 배치하고 확장
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # 스크롤바를 오른쪽에 배치
        self.canvas.configure(yscrollcommand=scrollbar.set)  # 캔버스와 스크롤바 연결

        self.inner_frame = ttk.Frame(self.canvas)  # 캔버스 내에 내부 프레임 생성
        self.inner_frame.columnconfigure(0, weight=1)  # 내부 프레임의 첫 번째 열 가중치 설정
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor=tk.NW,  # 캔버스에 내부 프레임을 창으로 추가
                                                       width=self.canvas.winfo_width())  # 캔버스 너비 설정

        self.canvas.bind('<Configure>', self._on_canvas_configure)  # 캔버스 크기 조정 시 이벤트 바인딩
        self.bind_all("<MouseWheel>", self._on_mousewheel)  # 마우스 휠 이벤트 바인딩
        self.bind_all("<Button-4>", self._on_mousewheel)  # Linux에서 마우스 버튼 4 이벤트 바인딩
        self.bind_all("<Button-5>", self._on_mousewheel)  # Linux에서 마우스 버튼 5 이벤트 바인딩

        self.after(100, self.check_update)  # 100ms 후 check_update 메서드 호출

    def _on_canvas_configure(self, event):  # 캔버스 크기 조정 이벤트 처리
        self.canvas.itemconfig(self.canvas_window, width=event.width)  # 캔버스 창의 너비 설정
        self._update_scroll_region()  # 스크롤 영역 업데이트

    def _update_scroll_region(self):  # 스크롤 영역 업데이트 메서드
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))  # 모든 항목의 경계 상자에 따라 스크롤 영역 설정

    def _on_mousewheel(self, event):  # 마우스 휠 이벤트 처리
        if event.num == 5 or event.delta < 0:  # 아래로 스크롤
            self.canvas.yview_scroll(1, "units")  # 캔버스를 1단위 아래로 스크롤
        elif event.num == 4 or event.delta > 0:  # 위로 스크롤
            self.canvas.yview_scroll(-1, "units")  # 캔버스를 1단위 위로 스크롤

    def check_update(self) -> None:  # UI 업데이트 확인 메서드
        try:
            while True:  # 무한 루프
                course = self.queue.get_nowait()  # 큐에서 과제 가져오기 (비어있으면 예외 발생)
                self.update_ui(course)  # UI 업데이트
                self._update_scroll_region()  # 스크롤 영역 업데이트
        except Empty:  # 큐가 비어있을 경우
            pass  # 아무 작업도 하지 않음
        finally:
            self.after(100, self.check_update)  # 100ms 후 다시 check_update 호출

    def start(self):  # GUI 시작 메서드
        try:
            self.mainloop()  # tkinter 메인 루프 시작
        finally:
            print("GUI closing...")  # GUI 종료 시 메시지 출력

    def update_ui(self, course: Course) -> None:  # UI 업데이트 메서드
        updated = False  # 업데이트 여부 플래그 초기화
        new_assignments = {}  # 새로운 과제를 저장할 딕셔너리 초기화

        for assignment in course.assignments.values():  # 과제 목록을 순회
            new_assignments[assignment.id] = assignment  # 새로운 과제 추가
            if (assignment.id not in self.current_assignments or  # 현재 과제에 없거나
                    self._is_assignment_changed(self.current_assignments[assignment.id], assignment)):  # 과제가 변경된 경우
                updated = True  # 업데이트 플래그 설정

        if updated:  # 업데이트가 필요한 경우
            for widget in self.inner_frame.winfo_children():  # 내부 프레임의 모든 위젯을 순회
                widget.destroy()  # 위젯 제거

            for i, assignment in enumerate(sorted(new_assignments.values(), key=lambda x: x.end_date or datetime.max)):  # 새로운 과제를 정렬하여 추가
                self._create_assignment_frame(i, assignment)  # 과제 프레임 생성

        self.current_assignments = new_assignments  # 현재 과제 업데이트
        self._update_scroll_region()  # 스크롤 영역 업데이트

    def _is_assignment_changed(self, old: BaseAssignment, new: BaseAssignment) -> bool:  # 과제 변경 여부 확인 메서드
        return (old.url != new.url or  # URL이 변경되었는지 확인
                old.title != new.title or  # 제목이 변경되었는지 확인
                old.status != new.status or  # 상태가 변경되었는지 확인
                old.start_date != new.start_date or  # 시작일이 변경되었는지 확인
                old.end_date != new.end_date)  # 종료일이 변경되었는지 확인

    def _create_assignment_frame(self, index: int, assignment: BaseAssignment) -> None:  # 과제 프레임 생성 메서드
        task_frame = ttk.Frame(self.inner_frame, padding=10)  # 과제 프레임 생성
        task_frame.grid(row=index, column=0, pady=5, sticky=tk.EW)  # 그리드에 배치

        # 열 구성
        task_frame.columnconfigure(0, weight=1)  # 제목 열 - 확장 가능
        task_frame.columnconfigure(1, minsize=300)  # 오른쪽 요소의 고정 너비

        def make_url_opener(url):  # URL을 여는 함수 생성
            return lambda: webbrowser.open(f'js로 쿠키 추가하기 {url}')  # 웹 브라우저에서 URL 열기

        # 날짜 문자열 생성
        date_str = f"{assignment.start_date.strftime('%Y-%m-%d')} ~ {assignment.end_date.strftime('%Y-%m-%d')}" if assignment.start_date and assignment.end_date else "날짜 미정"

        dday = ""  # D-day 문자열 초기화
        if assignment.end_date:  # 종료일이 있는 경우
            days_left = (assignment.end_date.date() - datetime.now().date()).days  # 남은 일수 계산
            if days_left > 0:  # 남은 일수가 양수인 경우
                dday = f"D-{days_left}"  # D-일수 형식으로 설정
            elif days_left == 0:  # 남은 일수가 0인 경우
                dday = "D-Day"  # D-Day로 설정
            else:  # 남은 일수가 음수인 경우
                dday = f"D+{abs(days_left)}"  # D+일수 형식으로 설정

        detail = f"상태: {assignment.status.value if assignment.status else '상태 미정'}"  # 상태 문자열 생성
        if isinstance(assignment, VideoAssignment):  # 비디오 과제인 경우
            detail += f" | 진행률: {assignment.progress}%"  # 진행률 추가

        # 왼쪽 부분 (제목 및 날짜)
        left_frame = ttk.Frame(task_frame)  # 왼쪽 프레임 생성
        left_frame.grid(row=0, column=0, sticky=tk.EW, padx=10)  # 그리드에 배치

        title_label = ttk.Label(left_frame, text=assignment.title, font=("Arial", 30))  # 제목 레이블 생성
        title_label.pack(anchor=tk.W)  # 왼쪽 정렬로 배치

        ttk.Label(left_frame, text=date_str, font=("Arial", 15, "italic")).pack(anchor=tk.W)  # 날짜 레이블 생성 및 배치

        # 오른쪽 부분 컨테이너
        right_frame = ttk.Frame(task_frame)  # 오른쪽 프레임 생성
        right_frame.grid(row=0, column=1, sticky=tk.E)  # 그리드에 배치

        # 상태
        status_label = ttk.Label(right_frame, text=detail, font=("Arial", 15))  # 상태 레이블 생성
        status_label.pack(side=tk.LEFT, padx=(0, 10))  # 왼쪽에 배치

        # D-day
        dday_label = ttk.Label(right_frame, text=dday, font=("Arial", 20, "bold"))  # D-day 레이블 생성
        dday_label.pack(side=tk.LEFT, padx=(0, 10))  # 왼쪽에 배치

        # 강의실 버튼
        classroom_btn = ttk.Button(right_frame, text="강의실", width=6,  # 강의실 버튼 생성
                                   command=make_url_opener(assignment.url))  # URL 열기 명령 설정
        classroom_btn.pack(side=tk.LEFT, padx=(0, 10))  # 왼쪽에 배치

@inject  # 의존성 주입을 위한 데코레이터
def gui_main(queue: Queue):  # GUI 메인 함수
    gui = GUI(queue)  # GUI 인스턴스 생성
    gui.start()  # GUI 시작
