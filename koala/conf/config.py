"""설정 관련 컨테이너 모듈"""  # 이 모듈은 애플리케이션의 설정을 관리하는 컨테이너를 정의합니다.
import sys
from pathlib import Path
from random import randint
from typing import Dict, Any

import yaml

from koala.conf.settings import Config, PortalConfig, DEFAULT_TIMEZONE


class ConfigParser:
    """YAML 설정 파일 파서"""

    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """YAML 파일 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"설정 파일 로드 실패: {e}")


class ConfigContainer:
    """설정 컨테이너"""

    def __init__(self):
        self.config_path = self._get_config_path()
        self.config = self._load_config()

    def _get_config_path(self) -> str:
        """실행 환경에 따른 기본 설정 파일 경로 반환"""
        if getattr(sys, 'frozen', False):
            # 실행 파일로 빌드된 경우
            base_path = Path(sys.executable).parent
        else:
            # 개발 중 실행하는 경우
            base_path = Path(__file__).parent.parent.parent

        return str(base_path / "config.yml")

    def _load_config(self) -> Config:
        """설정 로드 및 초기화"""
        config_data = ConfigParser.load_yaml(self.config_path)

        portal_config = PortalConfig(
            id=config_data['portal']['id'],
            password=config_data['portal']['password'],
            ip=f'203.255.221.{randint(0, 255)}'
        )

        config = Config(
            portal=portal_config,
            timezone=config_data.get('timezone', DEFAULT_TIMEZONE)
        )

        if not config.validate():
            raise ValueError("잘못된 설정입니다.")

        return config


__all__ = (  # 모듈에서 공개할 객체 목록
    'ConfigContainer',  # ConfigContainer 클래스 공개
)
