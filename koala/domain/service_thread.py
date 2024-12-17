import threading
from queue import Queue
from typing import Callable


class ServiceThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.queue = Queue()
        self.is_running = True

    def run(self):
        """서비스 작업 처리"""
        while self.is_running:
            try:
                task = self.queue.get()
                if task is not None:
                    task()
                self.queue.task_done()
            except Exception as e:
                print(f"서비스 작업 처리 중 오류: {e}")

    def execute(self, task: Callable):
        """서비스 작업 실행 요청"""
        self.queue.put(task)

    def stop(self):
        """스레드 종료"""
        self.is_running = False
        self.queue.put(None)  # 종료 신호
        self.join(timeout=1.0)
