"""인증 관련 모델 클래스 모듈"""

from typing import Dict, override

from aiohttp.abc import AbstractCookieJar


class Cookies(Dict[str, str]):
    """
    aiohttp의 비동기 쿠키인 AbstractCookieJar 쿠키를 동기 쿠키로 래핑한 쿠킹
    """
    @override
    def update(self, m, **kwargs) -> None:
        if not isinstance(m, AbstractCookieJar):
            super().update(m, **kwargs)

        super().update((cookie.key, cookie.value) for cookie in m)


__all__ = (
    'Cookies',
)
