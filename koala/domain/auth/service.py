from datetime import datetime

from aiohttp import ClientSession
from pytz.tzinfo import DstTzInfo

from koala.domain.auth.model import Cookies


class LoginService:

    def __init__(self,
                 portal_id: str,
                 portal_pw: str,
                 portal_ip: str,
                 cookies: Cookies,
                 timezone: DstTzInfo
                 ):
        self._portal_id = portal_id
        self._portal_pw = portal_pw
        self._portal_ip = portal_ip
        self._cookies = cookies
        self._timezone = timezone
        self._headers = {
            "X-Forwarded-For": self._portal_ip,
            "X-Real-IP": self._portal_ip,
        }

    async def login(self):
        """
        로그인을 시도한다.
        """
        print('[LoginService] Try Login')

        async with ClientSession(cookies=self._cookies) as session:
            await session.post(
                url='https://portal.koreatech.ac.kr/ktp/login/checkLoginId.do',
                allow_redirects=True,
                headers=self._headers,
                data={
                    'login_id': self._portal_id,
                    'login_pwd': self._portal_pw,
                }
            )

            session.cookie_jar.update_cookies({'kut_login_type': 'id'})

            await session.post(
                url="https://portal.koreatech.ac.kr/ktp/login/checkSecondLoginCert.do",
                allow_redirects=True,
                headers=self._headers,
                data={
                    'login_id': self._portal_id
                }
            )

            # SSO 인증
            await session.post(
                url="https://portal.koreatech.ac.kr/exsignon/sso/sso_assert.jsp",
                allow_redirects=True,
                headers=self._headers
            )

            # LMS 접근 -> Session 발급
            await session.get(
                url="https://el2.koreatech.ac.kr",
                allow_redirects=True,
                headers=self._headers
            )

            self._cookies.update(session.cookie_jar)

        print('[LoginService] Login Success')

    async def refresh(self):
        """
        로그인 세션을 갱신한다.

        POST https://portal.koreatech.ac.kr/proc/com.ServerTime.do

        세션을 갱신 하는데 사용된다. 내 기기의 타임 스탬프를 찍어도 된다.

        Unix Timestamp: 1970년 1월 1일 00:00:00 UTC를 기준점(0)으로 하여 경과된 초(seconds)를 나타낸다.
        """

        print('[LoginService] Try Refresh')

        timestamp = int(datetime.now(self._timezone).timestamp())

        async with ClientSession(cookies=self._cookies) as session:
            await session.post(
                url=f'https://portal.koreatech.ac.kr/eXPortal/common/common.jsp?timeStamp={timestamp}',
                allow_redirects=True,
                headers=self._headers,
            )

            self._cookies.update(session.cookie_jar)

        print('[LoginService] Refresh Success')


__all__ = (
    'LoginService',
)
