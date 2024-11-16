from http.cookies import SimpleCookie


class LoginService:

    def __init__(self,
                 portal_id: str,
                 portal_pw: str,
                 portal_ip: str,
                 cookie: SimpleCookie
                 ):
        self.portal_id = portal_id
        self.portal_pw = portal_pw
        self.portal_ip = portal_ip
        self.cookie = cookie

    async def login(self):
        print('[LoginService] Login')

    async def refresh(self):
        print('[LoginService] Cookie refresh')


__all__ = (
    'LoginService',
)
