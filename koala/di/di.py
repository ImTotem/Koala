from dependency_injector import containers, providers

from koala.conf.config import ConfigContainer
from koala.di.auth import _AuthContainer


class DI(containers.DeclarativeContainer):
    config = providers.Container(ConfigContainer).config

    auth = providers.Container(
        _AuthContainer,
        config=config.portal,
    )


__all__ = (
    'DI',
)
