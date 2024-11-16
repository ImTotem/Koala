from pydantic import field_validator
from pydantic_settings import BaseSettings
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError
from pytz.tzinfo import DstTzInfo


class PortalConfig(BaseSettings):
    id: str
    password: str
    ip: str


class Config(BaseSettings):
    portal: PortalConfig
    timezone: DstTzInfo = timezone('Asia/Seoul')

    @field_validator('timezone', mode='before')
    def validate_timezone(cls, zone: str) -> DstTzInfo:
        try:
            return timezone(zone)
        except UnknownTimeZoneError:
            return timezone('Asia/Seoul')


__all__ = (
    'PortalConfig',
    'Config',
)
