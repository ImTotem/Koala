from queue import Queue
from typing import List, Tuple

from koala.batch.core.result_collector import ResultCollector
from koala.batch.core.worker import Worker
from koala.batch.models.work_item import WorkItem


class WorkerPool:
    def __init__(self, result_collector: ResultCollector, num_workers: int = 4):
        self.result_collector = result_collector
        self.num_workers = num_workers
        self.queue = Queue()
        self.workers: List[Worker] = []

    def start(self) -> None:
        """워커 풀 시작"""
        # Worker 생성 및 시작
        for i in range(self.num_workers):
            worker = Worker(f"Worker-{i}", self.queue, self.result_collector)
            worker.start()
            self.workers.append(worker)

        print(f"Started WorkerPool with {self.num_workers} workers")

    def stop(self) -> None:
        """워커 풀 정지"""
        # 모든 워커 정지
        for worker in self.workers:
            worker.stop()

        # 워커 스레드 종료 대기
        for worker in self.workers:
            worker.join()

        self.workers.clear()
        print("WorkerPool stopped")

    def extend_works(self, works: Tuple[WorkItem, ...]) -> None:
        """여러 WorkItem을 우선순위 큐에 추가"""
        for work in works:
            self.queue.put(work)
            print(f"Added work item: {work.type.name}")
