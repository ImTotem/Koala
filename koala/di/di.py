"""의존성 주입 컨테이너 모듈

전체 애플리케이션의 의존성을 관리하는 메인 컨테이너
"""

from dependency_injector import containers, providers

from koala.conf.config import ConfigContainer
from koala.di.assignment import _AssignmentContainer
from koala.di.auth import _AuthContainer
from koala.domain.scheduler.manager import ScheduleManager


class DI(containers.DeclarativeContainer):
    """메인 의존성 주입 컨테이너.

    :ivar config: 설정 컨테이너
    :type config: providers.Container
    :ivar auth: 인증 관련 컨테이너
    :type auth: providers.Container
    :ivar schedule_manager: 스케줄 관리자 싱글톤
    :type schedule_manager: providers.ThreadSafeSingleton
    """

    config = providers.Container(ConfigContainer).config

    auth = providers.Container(
        _AuthContainer,
        config=config,
    )

    assignment = providers.Container(
        _AssignmentContainer,
        config=config,
        cookies=auth.cookies,
    )

    schedule_manager = providers.ThreadSafeSingleton(
        ScheduleManager,
        login_service=auth.service,
        assignment_service=assignment.service,
    )


__all__ = (
    'DI',
)
