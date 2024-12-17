"""포털 로그인 서비스 모듈"""

from datetime import datetime

import requests
from pytz.tzinfo import DstTzInfo
from requests.cookies import RequestsCookieJar


class AuthService:
    """포털 로그인 서비스

    :param portal_id: 포털 아이디
    :type portal_id: str
    :param portal_pw: 포털 비밀번호
    :type portal_pw: str
    :param portal_ip: 포털 접속 IP
    :type portal_ip: str
    :param cookies: 쿠키 저장소
    :type cookies: Cookies
    :param timezone: 타임존 정보
    :type timezone: DstTzInfo
    """

    def __init__(self,
                 portal_id: str,
                 portal_pw: str,
                 portal_ip: str,
                 cookies: RequestsCookieJar,
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

    def get_cookies(self):
        return self._cookies

    def login(self):
        """포털 로그인을 수행한다.

        :raises requests.RequestException: HTTP 요청 실패시 발생
        """
        print('[AuthService] Try Login')

        with requests.Session() as session:
            # 로그인 체크
            session.post(
                url='https://portal.koreatech.ac.kr/ktp/login/checkLoginId.do',
                headers=self._headers,
                data={
                    'login_id': self._portal_id,
                    'login_pwd': self._portal_pw,
                },
                allow_redirects=True
            )

            session.cookies.set('kut_login_type', 'id')

            # 2차 인증
            session.post(
                url="https://portal.koreatech.ac.kr/ktp/login/checkSecondLoginCert.do",
                headers=self._headers,
                data={
                    'login_id': self._portal_id
                },
                allow_redirects=True
            )

            # SSO 인증
            session.post(
                url="https://portal.koreatech.ac.kr/exsignon/sso/sso_assert.jsp",
                headers=self._headers,
                allow_redirects=True
            )

            # LMS 접근 -> Session 발급
            session.get(
                url="https://el2.koreatech.ac.kr",
                headers=self._headers,
                allow_redirects=True
            )

            self._cookies.update(session.cookies)

        print('[AuthService] Login Success')

    def refresh(self):
        """
        로그인 세션을 갱신한다.

        POST https://portal.koreatech.ac.kr/proc/com.ServerTime.do

        세션을 갱신 하는데 사용된다. 내 기기의 타임 스탬프를 찍어도 된다.

        Unix Timestamp: 1970년 1월 1일 00:00:00 UTC를 기준점(0)으로 하여 경과된 초(seconds)를 나타낸다.
        """
        print('[AuthService] Try Refresh')

        timestamp = int(datetime.now(self._timezone).timestamp())

        with requests.Session() as session:
            session.cookies.update(self._cookies)

            session.post(
                url=f'https://portal.koreatech.ac.kr/eXPortal/common/common.jsp?timeStamp={timestamp}',
                headers=self._headers,
                allow_redirects=True
            )

            self._cookies.update(session.cookies)

        print('[AuthService] Refresh Success')


__all__ = (
    'AuthService',
)
