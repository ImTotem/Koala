"""프로그램 시작점

진입점을 통해 시작되는 메인 부분
"""
from koala.conf import ConfigContainer
from koala.domain.assignment.service import AssignmentService
from koala.domain.auth.service import AuthService
from koala.domain.notification_manager import NotificationManager
from koala.domain.view.gui import GUI
from requests.cookies import RequestsCookieJar


# 프로그램 실행 함수
def run() -> None:
    config = ConfigContainer().config
    cookies: RequestsCookieJar = RequestsCookieJar()

    GUI(
        auth_service=AuthService(
            portal_id=config.portal.id,
            portal_pw=config.portal.password,
            portal_ip=config.portal.ip,
            cookies=cookies,
            timezone=config.tz
        ),
        assignment_service=AssignmentService(
            cookies=cookies
        ),
        notification_manager=NotificationManager()
    ).start()
