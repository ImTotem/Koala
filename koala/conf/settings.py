"""설정 유효성 검사용"""  # 설정 파일의 목적을 설명하는 주석

from pydantic import field_validator  # Pydantic의 필드 검증기를 가져옴
from pydantic_settings import BaseSettings  # Pydantic의 기본 설정 클래스를 가져옴
from pytz import timezone  # pytz에서 시간대 관련 기능을 가져옴
from pytz.exceptions import UnknownTimeZoneError  # 알 수 없는 시간대 예외를 가져옴
from pytz.tzinfo import DstTzInfo  # DST 시간대 정보를 가져옴


class PortalConfig(BaseSettings):  # PortalConfig 클래스 정의, BaseSettings를 상속
    id: str  # 포털 ID를 나타내는 문자열 필드
    password: str  # 포털 비밀번호를 나타내는 문자열 필드
    ip: str  # 포털 IP 주소를 나타내는 문자열 필드


class Config(BaseSettings):  # Config 클래스 정의, BaseSettings를 상속
    portal: PortalConfig  # PortalConfig 인스턴스를 포함하는 필드
    timezone: DstTzInfo = timezone('Asia/Seoul')  # 기본 시간대를 'Asia/Seoul'로 설정

    @field_validator('timezone', mode='before')  # 'timezone' 필드에 대한 검증기 정의
    def validate_timezone(cls, zone: str) -> DstTzInfo:  # 검증기 메서드 정의
        try:
            return timezone(zone)  # 주어진 시간대 문자열로 시간대 객체 생성
        except UnknownTimeZoneError:  # 알 수 없는 시간대 예외 처리
            return timezone('Asia/Seoul')  # 기본 시간대인 'Asia/Seoul' 반환


__all__ = (  # 모듈에서 공개할 객체를 정의
    'PortalConfig',  # PortalConfig 클래스를 공개
    'Config',  # Config 클래스를 공개
)
