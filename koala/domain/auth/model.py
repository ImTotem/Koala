from typing import Dict, override

from aiohttp.abc import AbstractCookieJar


class Cookies(Dict[str, str]):

    @override
    def update(self, m, **kwargs) -> None:
        if not isinstance(m, AbstractCookieJar):
            super().update(m, **kwargs)

        super().update((cookie.key, cookie.value) for cookie in m)


__all__ = (
    'Cookies',
)
