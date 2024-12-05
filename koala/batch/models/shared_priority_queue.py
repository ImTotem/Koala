import threading
from queue import PriorityQueue, Empty
from typing import Optional, Any


class SharedPriorityQueue(PriorityQueue):
    def __init__(self):
        super().__init__()
        self.prev: Optional[Any] = None
        self.prev_lock = threading.Lock()  # prev 접근을 위한 lock 추가

    def get(self, block=True, timeout=None):
        """현재 처리 가능한 작업 가져오기"""
        with self.prev_lock:  # prev 접근 동기화
            if self.prev is None:
                self.prev = super().get(block=block, timeout=timeout)
                return self.prev

            if self.empty() or (self.prev.priority < self.queue[0].priority):
                raise Empty()

            self.prev = super().get(block=block, timeout=timeout)
            return self.prev

    def task_done(self):
        """작업 완료"""
        super().task_done()
        with self.prev_lock:  # prev 접근 동기화
            self.prev = None
