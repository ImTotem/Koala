import asyncio  # 비동기 프로그래밍을 위한 asyncio 모듈을 임포트
import threading  # 스레드를 다루기 위한 threading 모듈을 임포트
from queue import Empty, Queue  # 큐를 사용하기 위한 Empty 예외와 Queue 클래스를 임포트
from typing import Optional  # Optional 타입을 사용하기 위한 임포트

from koala.batch.core.result_collector import ResultCollector  # 작업 결과를 수집하기 위한 ResultCollector 클래스 임포트
from koala.batch.models.work_item import WorkItem, WorkResult  # 작업 항목과 작업 결과 관련 클래스 임포트

class Worker(threading.Thread):  # threading.Thread를 상속받아 Worker 클래스를 정의
    def __init__(  # 생성자 메서드 정의
            self,
            name: str,  # 워커의 이름
            queue: Queue,  # 작업을 받을 큐
            result_collector: ResultCollector  # 작업 결과를 수집할 ResultCollector 인스턴스
    ):
        super().__init__()  # 부모 클래스의 생성자 호출
        self.name = name  # 워커 이름 초기화
        self.queue = queue  # 큐 초기화
        self.result_collector = result_collector  # 결과 수집기 초기화
        self.daemon = True  # 메인 스레드 종료 시 함께 종료되도록 설정
        self.running = False  # 워커 실행 상태 초기화
        self.loop: Optional[asyncio.AbstractEventLoop] = None  # 비동기 이벤트 루프 초기화

    def run(self) -> None:  # 스레드 실행 메서드 정의
        """Thread run 메서드 구현"""
        self.running = True  # 워커 실행 상태를 True로 설정
        self.loop = asyncio.new_event_loop()  # 새로운 비동기 이벤트 루프 생성
        asyncio.set_event_loop(self.loop)  # 현재 스레드에 이벤트 루프 설정

        print(f"{self.name} started")  # 워커 시작 메시지 출력
        self.loop.run_until_complete(self._process_queue())  # 큐 처리 메서드 ��행

        try:
            print(f"{self.name} started")  # 워커 시작 메시지 출력
            self.loop.run_until_complete(self._process_queue())  # 큐 처리 메서드 실행
        except Exception as e:  # 예외 처리
            print(f"{self.name} error: {e}")  # 오류 메시지 출력
        finally:
            self.loop.close()  # 이벤트 루프 종료
            print(f"{self.name} stopped")  # 워커 종료 메시지 출력

    def stop(self) -> None:  # 워커 정지 메서드 정의
        """워커 정지"""
        self.running = False  # 워커 실행 상태를 False로 설정
        if self.loop and self.loop.is_running():  # 이벤트 루프가 존재하고 실행 중일 경우
            self.loop.stop()  # 이벤트 루프 정지

    async def _process_queue(self) -> None:  # 큐에서 작업을 가져와 처리하는 비동기 메서드
        """큐에서 작업을 가져와 처리"""
        while self.running:  # 워커가 실행 중인 동안
            try:
                # 1초 동안 기다리고, 작업이 없으면 Empty 예외 발생
                work_item = self.queue.get(block=True, timeout=1.0)  # 큐에서 작업 항목 가져오기
                print(f"{self.name} got work item: {work_item.type.name}")  # 작업 항목 수신 메시지 출력

                # 작업 실행
                await self._execute_work(work_item)  # 작업 실행 메서드 호출

                # 작업 완료 표시
                self.queue.task_done()  # 큐에서 작업 완료 표시

            except Empty:  # 큐가 비어있을 경우
                # timeout이 지나도 작업이 없는 경우 - 정상적인 상황
                continue  # 다음 반복으로 넘어감
            except Exception as e:  # 다른 예외 발생 시
                print(f"{self.name} error in process_queue: {e}")  # 오류 메시지 출력
                continue  # 다음 반복으로 넘어감

    async def _execute_work(self, work_item: WorkItem) -> None:  # 작업 항목을 실행하는 비동기 메서드
        """WorkItem 실행"""
        try:
            print(f"{self.name} executing {work_item.type.name}")  # 작업 실행 메시지 출력

            if hasattr(work_item, 'arguments') and work_item.arguments:  # 작업 항목에 인자가 있는 경우
                method_result = await work_item.method(*work_item.arguments)  # 메서드 실행
            else:  # 인자가 없는 경우
                method_result = await work_item.method()  # 메서드 실행

            result = WorkResult(  # 작업 결과 객체 생성
                work_type=work_item.type,  # 작업 유형 설정
                success=True  # 성공 여부 설정
            )

            if method_result is not None:  # 메서드 결과가 있는 경우
                result.updated = method_result  # 업데이트된 결과 설정
                result.course = work_item.arguments[0]  # 첫 번째 인자를 과목으로 설정

            self.result_collector.add_result(result)  # 결과 수집기에 결과 추가

            print(f"{self.name} completed {work_item.type.name}")  # 작업 완료 메시지 출력

        except Exception as e:  # 예외 발생 시
            self.result_collector.add_result(WorkResult(  # 실패한 작업 결과 추가
                work_type=work_item.type,  # 작업 유형 설정
                success=False,  # 실패 여부 설정
                error=e  # 오류 정보 설정
            ))

            print(f"{self.name} failed to execute {work_item.type.name}: {e}")  # 실패 메시지 출력
            raise  # 예외 재발생
