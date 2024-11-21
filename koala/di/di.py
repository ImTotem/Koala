from dependency_injector import containers, providers

from koala.conf.config import ConfigContainer
from koala.di.auth import _AuthContainer
from koala.domain.scheduler.manager import ScheduleManager


class DI(containers.DeclarativeContainer):
    config = providers.Container(ConfigContainer).config

    auth = providers.Container(
        _AuthContainer,
        config=config,
    )

    schedule_manager = providers.ThreadSafeSingleton(
        ScheduleManager,
        login_service=auth.service,
    )


__all__ = (
    'DI',
)
