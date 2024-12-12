from multiprocessing import Queue  # 멀티프로세싱을 위한 Queue 클래스 임포트
from typing import Set  # 집합(Set) 타입을 사용하기 위한 임포트

from koala.batch.models.work_item import WorkResult, WorkType  # 작업 결과 및 작업 유형 관련 클래스 임포트
from koala.domain.assignment.dto import AssignmentDTO
from koala.domain.assignment.model import Course  # Course 모델 클래스 임포트
from koala.utils import Subject  # 옵저버 패턴을 위한 Subject 클래스 임포트


class ResultCollector(Subject):  # Subject 클래스를 상속받아 ResultCollector 클래스 정의

    def __init__(self, courses: Set[Course], queue: Queue):  # 생성자, courses와 queue를 인자로 받음
        super().__init__()  # 부모 클래스의 생성자 호출
        self.pending_courses: int = 0  # 대기 중인 과목 수 초기화
        self.courses = courses  # 인자로 받은 courses를 인스턴스 변수에 저장
        self.queue = queue  # 인자로 받은 queue를 인스턴스 변수에 저장

    def add_result(self, result: WorkResult) -> None:  # 작업 결과를 추가하는 메서드
        """작업 결과 추가 및 BatchManager에 알림"""
        if result.work_type != WorkType.ASSIGNMENT:  # 작업 유형이 ASSIGNMENT가 아닐 경우
            # 일반 작업은 바로 완료 알림
            self.notify()  # 모든 옵저버에게 알림
            return  # 메서드 종료

        self.pending_courses += 1  # 대기 중인 과목 수 증가

        if result.updated:  # 결과가 업데이트된 경우
            # TODO : dto 변환
            # AssignmentDTO.factory(result.course.assignments[0])
            self.queue.put(result.course)  # 큐에 과목 추가

        if self.pending_courses == len(self.courses):  # 대기 중인 과목 수가 전체 과목 수와 같을 경우
            self.pending_courses = 0  # 대기 중인 과목 수 초기화
            self.notify()  # 모든 옵저버에게 알림
