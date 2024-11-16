from http.cookies import SimpleCookie

from dependency_injector import containers, providers

from koala.domain.auth.service import LoginService


class _AuthContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    cookie = providers.ThreadSafeSingleton(SimpleCookie)

    service = providers.ThreadSafeSingleton(
        LoginService,
        portal_id=config.id,
        portal_pw=config.password,
        portal_ip=config.ip,
        cookie=cookie,
    )


__all__ = (
    '_AuthContainer',
)
