import asyncio
import threading

import schedule


class ScheduleThread(threading.Thread):
    def __init__(self, schedules, daemon=True):
        super().__init__(daemon=daemon)
        self._schedules = schedules
        self._stop_event = threading.Event()
        self._loop = None

    def _create_task(self, func, *args, **kwargs):
        self._loop.create_task(func(*args, **kwargs))

    def start(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # 스케줄 등록
        for job_func, interval in self._schedules:
            schedule.every(interval).seconds.do(self._create_task, job_func)

        super().start()

    def run(self):
        # 메인 루프
        while not self._stop_event.is_set():
            schedule.run_pending()
            self._loop.run_until_complete(asyncio.sleep(1))

        super().run()
