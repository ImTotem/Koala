"""설정 관련 컨테이너 모듈"""  # 이 모듈은 애플리케이션의 설정을 관리하는 컨테이너를 정의합니다.

from pathlib import Path  # 파일 경로 작업을 위한 Path 클래스 임포트
from random import randint  # 랜덤 정수를 생성하기 위한 randint 함수 임포트

from dependency_injector import containers, providers  # 의존성 주입을 위한 containers와 providers 임포트

from koala.conf.settings import PortalConfig, Config  # 설정 관련 클래스 임포트


class ConfigContainer(containers.DeclarativeContainer):  # 의존성 주입을 위한 설정 컨테이너 클래스 정의
    config = providers.Configuration()  # Configuration 객체를 제공하는 프로바이더 정의

    config.from_yaml(  # YAML 파일에서 설정을 로드
        str(Path(__file__).parent.parent.parent / "config.yml"),  # config.yml 파일의 경로 설정
        required=True  # 필수 설정으로 지정
    )

    config.portal.from_dict({  # portal 설정을 딕셔너리에서 로드
        'ip': f'203.255.221.{randint(0, 255)}',  # 랜덤한 IP 주소 생성
    })

    config.from_dict(  # Config 객체를 딕셔너리에서 로드
        Config(  # Config 클래스의 인스턴스 생성
            portal=PortalConfig(  # PortalConfig 객체 생성
                id=config.portal.id(),  # portal ID 설정
                password=config.portal.password(),  # portal 비밀번호 설정
                ip=config.portal.ip()  # portal IP 설정
            ),
            timezone=config.timezone()  # 타임존 설정
        ).model_dump()  # 모델을 딕셔너리 형태로 변환
    )


__all__ = (  # 모듈에서 공개할 객체 목록
    'ConfigContainer',  # ConfigContainer 클래스 공개
)
