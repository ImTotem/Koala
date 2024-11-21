"""설정 관련 컨테이너 모듈"""

from pathlib import Path
from random import randint

from dependency_injector import containers, providers

from koala.conf.settings import PortalConfig, Config


class ConfigContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    config.from_yaml(
        str(Path(__file__).parent.parent.parent / "config.yml"),
        required=True
    )

    config.portal.from_dict({
        'ip': f'203.255.221.{randint(0, 255)}',
    })

    config.from_dict(
        Config(
            portal=PortalConfig(
                id=config.portal.id(),
                password=config.portal.password(),
                ip=config.portal.ip()
            ),
            timezone=config.timezone()
        ).model_dump()
    )


__all__ = (
    'ConfigContainer',
)
