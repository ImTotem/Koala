from queue import Queue  # 작업을 처리하기 위한 큐 클래스를 임포트
from typing import List, Tuple  # 리스트와 튜플 타입을 사용하기 위한 임포트

from koala.batch.core.result_collector import ResultCollector  # 작업 결과를 수집하기 위한 ResultCollector 클래스 임포트
from koala.batch.core.worker import Worker  # 작업을 수행할 Worker 클래스 임포트
from koala.batch.models.work_item import WorkItem  # 작업 항목을 정의하는 WorkItem 클래스 임포트


class WorkerPool:  # 여러 워커를 관리하는 WorkerPool 클래스 정의
    def __init__(self, result_collector: ResultCollector, num_workers: int = 4):  # 생성자 메서드
        self.result_collector = result_collector  # 결과 수집기를 인스턴스 변수에 저장
        self.num_workers = num_workers  # 생성할 워커 수를 인스턴스 변수에 저장
        self.queue = Queue()  # 작업을 저장할 큐 초기화
        self.workers: List[Worker] = []  # 워커 목록 초기화

    def start(self) -> None:  # 워커 풀을 시작하는 메서드
        """워커 풀 시작"""
        # Worker 생성 및 시작
        for i in range(self.num_workers):  # 지정된 수의 워커를 생성
            worker = Worker(f"Worker-{i}", self.queue, self.result_collector)  # 워커 인스턴스 생성
            worker.start()  # 워커 스레드 시작
            self.workers.append(worker)  # 생성된 워커를 목록에 추가

        print(f"Started WorkerPool with {self.num_workers} workers")  # 시작된 워커 풀 정보 출력

    def stop(self) -> None:  # 워커 풀을 정지하는 메서드
        """워커 풀 정지"""
        # 모든 워커 정지
        for worker in self.workers:  # 모든 워커에 대해
            worker.stop()  # 각 워커를 정지

        # 워커 스레드 종료 대기
        for worker in self.workers:  # 모든 워커에 대해
            worker.join()  # 각 워커가 종료될 때까지 대기

        self.workers.clear()  # 워커 목록 초기화
        print("WorkerPool stopped")  # 워커 풀 정지 메시지 출력

    def extend_works(self, works: Tuple[WorkItem, ...]) -> None:  # 여러 작업 항목을 큐에 추가하는 메서드
        """여러 WorkItem을 우선순위 큐에 추가"""
        for work in works:  # 주어진 작업 항목에 대해
            self.queue.put(work)  # 큐에 작업 항목 추가
            print(f"Added work item: {work.type.name}")  # 추가된 작업 항목 정보 출력
