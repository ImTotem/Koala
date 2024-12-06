import asyncio
import threading
from queue import Empty, Queue
from typing import Optional

from koala.batch.core.result_collector import ResultCollector
from koala.batch.models.work_item import WorkItem, WorkResult


class Worker(threading.Thread):
    def __init__(
            self,
            name: str,
            queue: Queue,
            result_collector: ResultCollector
    ):
        super().__init__()
        self.name = name
        self.queue = queue
        self.result_collector = result_collector
        self.daemon = True  # 메인 스레드 종료시 함께 종료
        self.running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def run(self) -> None:
        """Thread run 메서드 구현"""
        self.running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        print(f"{self.name} started")
        self.loop.run_until_complete(self._process_queue())

        try:
            print(f"{self.name} started")
            self.loop.run_until_complete(self._process_queue())
        except Exception as e:
            print(f"{self.name} error: {e}")
        finally:
            self.loop.close()
            print(f"{self.name} stopped")

    def stop(self) -> None:
        """워커 정지"""
        self.running = False
        if self.loop and self.loop.is_running():
            self.loop.stop()

    async def _process_queue(self) -> None:
        """큐에서 작업을 가져와 처리"""
        while self.running:
            try:
                # 1초 동안 기다리고, 작업이 없으면 Empty 예외 발생
                work_item = self.queue.get(block=True, timeout=1.0)
                print(f"{self.name} got work item: {work_item.type.name}")

                # 작업 실행
                await self._execute_work(work_item)

                # 작업 완료 표시
                self.queue.task_done()

            except Empty:
                # timeout이 지나도 작업이 없는 경우 - 정상적인 상황
                continue
            except Exception as e:
                print(f"{self.name} error in process_queue: {e}")
                continue

    async def _execute_work(self, work_item: WorkItem) -> None:
        """WorkItem 실행"""
        try:
            print(f"{self.name} executing {work_item.type.name}")

            if hasattr(work_item, 'arguments') and work_item.arguments:
                method_result = await work_item.method(*work_item.arguments)
            else:
                method_result = await work_item.method()

            result = WorkResult(
                work_type=work_item.type,
                success=True
            )

            if method_result is not None:
                result.updated = method_result
                result.course = work_item.arguments[0]

            self.result_collector.add_result(result)

            print(f"{self.name} completed {work_item.type.name}")

        except Exception as e:
            self.result_collector.add_result(WorkResult(
                work_type=work_item.type,
                success=False,
                error=e
            ))

            print(f"{self.name} failed to execute {work_item.type.name}: {e}")
            raise
