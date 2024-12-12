from dataclasses import dataclass, field  # dataclass와 field를 임포트하여 데이터 클래스를 정의
from enum import Enum, auto  # Enum과 auto를 임포트하여 열거형을 정의
from typing import Optional, Callable, Tuple  # Optional, Callable, Tuple 타입을 임포트

from koala.domain.assignment.model import Course  # Course 모델 클래스를 임포트

class WorkType(Enum):  # 작업 유형을 정의하는 열거형 클래스
    LOGIN = auto()  # 로그인 작업 유형
    REFRESH = auto()  # 세션 갱신 작업 유형
    COURSES = auto()  # 과정 목록 작업 유형
    ASSIGNMENT = auto()  # 과제 작업 유형

@dataclass(kw_only=True)  # 키워드 전용 인자를 사용하는 데이터 클래스 정의
class WorkItem:  # 작업 항목을 정의하는 클래스
    type: WorkType  # 작업 유형 (WorkType 열거형)
    interval: int  # 작업 실행 간격 (초 단위)
    method: Callable  # 실행할 메서드 (호출 가능한 객체)
    arguments: Tuple = field(default_factory=tuple)  # 메서드에 전달할 인자 (기본값은 빈 튜플)

@dataclass  # 데이터 클래스를 정의
class WorkResult:  # 작업 결과를 정의하는 클래스
    work_type: WorkType  # 작업 유형 (WorkType 열거형)
    success: bool  # 작업 성공 여부 (True/False)
    updated: bool = False  # 작업 결과가 업데이트되었는지 여부 (기본값은 False)
    course: Optional[Course] = None  # 작업과 관련된 Course 객체 (선택적)
    error: Optional[Exception] = None  # 작업 중 발생한 예외 (선택적)
