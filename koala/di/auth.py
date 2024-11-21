"""인증 관련 의존성 컨테이너 모듈"""

from dependency_injector import containers, providers

from koala.domain.auth.model import Cookies
from koala.domain.auth.service import LoginService


class _AuthContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    cookies = providers.ThreadSafeSingleton(Cookies)

    service = providers.ThreadSafeSingleton(
        LoginService,
        portal_id=config.portal.id,
        portal_pw=config.portal.password,
        portal_ip=config.portal.ip,
        cookies=cookies,
        timezone=config.timezone,
    )


__all__ = (
    '_AuthContainer',
)
