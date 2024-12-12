from collections import defaultdict  # 기본값이 있는 딕셔너리를 사용하기 위해 defaultdict 임포트
from dataclasses import dataclass, field  # 데이터 클래스를 정의하기 위해 dataclass와 field 임포트
from datetime import datetime  # 날짜와 시간을 다루기 위해 datetime 임포트
from enum import Enum  # 열거형을 정의하기 위해 Enum 임포트
from typing import DefaultDict, Union  # DefaultDict와 Union 타입을 사용하기 위해 임포트

class Status(Enum):  # 과제 상태를 정의하는 열거형 클래스
    오픈전 = '오픈전'  # 과제가 오픈되지 않은 상태
    진행중 = '진행중'  # 과제가 진행 중인 상태
    완료 = '종료'  # 과제가 완료된 상태
    지각 = '지각'  # 과제가 지각된 상태
    미제출 = '미제출'  # 과제가 제출되지 않은 상태
    비활성 = '비활성'  # 과제가 비활성화된 상태
    활성 = '활성'  # 과제가 활성화된 상태
    기한경과 = '기한경과'  # 과제가 기한을 초과한 상태

    @classmethod
    def from_string(cls, value: str) -> 'Status':  # 문자열로부터 Status 객체를 생성하는 클래스 메서드
        try:
            return cls(value)  # 주어진 문자열로 Status 객체 생성
        except ValueError:  # ValueError 발생 시
            try:
                return cls.__members__[value.upper()]  # 대문자로 변환하여 멤버 검색
            except KeyError:  # KeyError 발생 시
                raise ValueError(f"'{value}' is not a valid {cls.__name__}")  # 유효하지 않은 상태 메시지 발생

@dataclass  # 데이터 클래스를 정의
class BaseAssignment:  # 기본 과제 클래스를 정의
    _id: int  # 과제 ID
    url: str  # 과제 URL
    title: str  # 과제 제목
    status: Union[Status, None]  # 과제 상태 (Status 열거형 또는 None)
    start_date: Union[datetime, None]  # 시작 날짜 (datetime 또는 None)
    end_date: Union[datetime, None]  # 종료 날짜 (datetime 또는 None)

    @property
    def id(self):  # ID 속성
        return self._id  # 과제 ID 반환

    def update(self, other):  # 다른 BaseAssignment 객체로부터 업데이트하는 메서드
        if isinstance(other, BaseAssignment):  # 다른 객체가 BaseAssignment 인스턴스인지 확인
            updated = False  # 업데이트 여부 초기화
            if (self.url != other.url or  # URL이 다를 경우
                self.title != other.title or  # 제목이 다를 경우
                self.status != other.status or  # 상태가 다를 경우
                self.start_date != other.start_date or  # 시작 날짜가 다를 경우
                self.end_date != other.end_date):  # 종료 날짜가 다를 경우
                updated = True  # 업데이트 여부를 True로 설정

            self.url = other.url  # URL 업데이트
            self.title = other.title  # 제목 업데이트
            self.status = other.status  # 상태 업데이트
            self.start_date = other.start_date  # 시작 날짜 업데이트
            self.end_date = other.end_date  # 종료 날짜 업데이트

            return updated  # 업데이트 여부 반환

    def __hash__(self):  # 해시 메서드 정의
        return hash(self._id)  # 과제 ID의 해시값 반환

    def __eq__(self, other: object):  # 동등성 비교 메서드 정의
        return hash(self) == hash(other)  # 해시값을 비교하여 동등성 판단

@dataclass(eq=False)  # 동등성 비교를 False로 설정한 데이터 클래스 정의
class VideoAssignment(BaseAssignment):  # 비디오 과제 클래스를 정의
    progress: int  # 진행 상태를 나타내는 정수

QuizAssignment = BaseAssignment  # QuizAssignment를 BaseAssignment로 설정
AssignAssignment = BaseAssignment  # AssignAssignment를 BaseAssignment로 설정

@dataclass  # 데이터 클래스를 정의
class Course:  # 과정 클래스를 정의
    _id: int  # 과정 ID
    url: str  # 과정 URL
    name: str  # 과정 이름
    assignments: DefaultDict[int, BaseAssignment] = field(default_factory=lambda: defaultdict(BaseAssignment))  # 과제 목록 초기화

    @property
    def id(self):  # ID 속성
        return self._id  # 과정 ID 반환

    def update(self, other):  # 다른 객체로부터 업데이트하는 메서드
        if isinstance(other, BaseAssignment):  # 다른 객체가 BaseAssignment 인스턴스인지 확인
            if other in self.assignments:  # 과제가 존재할 경우
                return self.assignments[other.id].update(self.assignments)  # 과제 내용이 수정되었을 경우 True, 아니면 False
            else:  # 과제가 목록에 없는 경우
                self.assignments[other.id] = other  # 과제 추가
                return True  # 추가된 경우 True 반환
        elif isinstance(other, defaultdict):  # 다른 객체가 defaultdict인 경우
            updated = False  # 업데이트 여부 초기화
            for assignment in other.values():  # 모든 과제에 대해
                updated |= self.update(assignment)  # 업데이트 여부를 OR 연산하여 갱신

            return updated  # 업데이트 여부 반환
        elif isinstance(other, list):  # 다른 객체가 리스트인 경우
            updated = False  # 업데이트 여부 초기화
            for assignment in other:  # 모든 과제에 대해
                updated |= self.update(assignment)  # 업데이트 여부를 OR 연산하여 갱신

            return updated  # 업데이트 여부 반환

        return False  # 업데이트가 이루어지지 않은 경우 False 반환

    def __hash__(self):  # 해시 메서드 정의
        return hash(self._id)  # 과정 ID의 해시값 반환

    def __eq__(self, other):  # 동등성 비교 메서드 정의
        return hash(self) == hash(other)  # 해시값을 비교하여 동등성 판단