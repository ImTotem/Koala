"""스케쥴 매니저 모듈"""

from koala.domain.auth.service import LoginService
from koala.domain.scheduler.thread import ScheduleThread


class ScheduleManager:
    """
    주기적으로 동작해야하는 스케줄 관리

    관리 방법: self._schedules 에 (주기적으로 실행 할 함수, 주기(단위: 초))를 추가

    """

    def __init__(self,
                 login_service: LoginService,
                 ):
        self._login_service = login_service
        self._thread = None
        self._schedules = (  # (job_func, interval_seconds)
            (self._login_service.refresh, 3 * 60 * 60),
        )

    async def start(self):
        await self._login_service.login()

        self._thread = ScheduleThread(schedules=self._schedules, daemon=True)
        self._thread.start()


__all__ = (
    'ScheduleManager',
)
