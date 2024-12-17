"""설정 유효성 검사용"""  # 설정 파일의 목적을 설명하는 주석

from dataclasses import dataclass, field
from datetime import datetime

import pytz

DEFAULT_TIMEZONE = 'Asia/Seoul'


@dataclass
class PortalConfig:
    """포털 설정을 위한 데이터 클래스"""
    id: str
    password: str
    ip: str

    def validate(self) -> bool:
        """
        포털 설정의 유효성을 검사
        - id, password, ip가 모두 비어있지 않은지 확인
        - ip가 올바른 형식인지 확인
        """
        if not (self.id and self.password and self.ip):
            return False

        # IP 주소 형식 검증
        try:
            parts = self.ip.split('.')
            if len(parts) != 4:
                return False
            return all(0 <= int(part) <= 255 for part in parts)
        except (ValueError, AttributeError):
            return False


@dataclass
class Config:
    """애플리케이션 전체 설정을 위한 데이터 클래스"""
    portal: PortalConfig
    timezone: str
    _tz: pytz.timezone = field(init=False)

    def __post_init__(self):
        """timezone 문자열로부터 tz 객체 초기화"""
        try:
            self._tz = pytz.timezone(self.timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            self.timezone = DEFAULT_TIMEZONE
            self._tz = pytz.timezone(DEFAULT_TIMEZONE)

    @property
    def tz(self) -> pytz.timezone:
        return self._tz

    def get_current_time(self) -> datetime:
        """현재 시간을 설정된 timezone으로 반환"""
        return datetime.now(self.tz)

    def validate(self) -> bool:
        """
        전체 설정의 유효성 검사
        - portal 설정이 유효한지 확인
        - timezone이 올바르게 설정되었는지 확인
        """
        return self.portal.validate() and bool(self.tz)


__all__ = (  # 모듈에서 공개할 객체를 정의
    'PortalConfig',  # PortalConfig 클래스를 공개
    'Config',  # Config 클래스를 공개
    'DEFAULT_TIMEZONE'  # 기본 timezone을 공개
)
