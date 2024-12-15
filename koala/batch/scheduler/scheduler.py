import threading  # 스레딩을 위한 모듈 임포트
import time  # 시간 관련 기능을 위한 모듈 임포트

import schedule  # 작업 스케줄링을 위한 모듈 임포트

from koala.batch.core.batch_manager import BatchManager  # 배치 작업을 관리하는 BatchManager 클래스 임포트
from koala.batch.models.work_item import WorkItem, WorkType  # 작업 항목 및 작업 유형 관련 클래스 임포트
from koala.domain.assignment.service import AssignmentService  # 과제 서비스 관련 클래스 임포트
from koala.domain.auth.service import LoginService  # 로그인 서비스 관련 클래스 임포트


class Scheduler(threading.Thread):  # 스레드를 상속받아 Scheduler 클래스 정의
    def __init__(
            self,
            batch_manager: BatchManager,
            login_service: LoginService,
            assignment_service: AssignmentService
    ):
        super().__init__(daemon=False)  # 스레드 초기화, daemon=False로 설정하여 메인 스레드 종료 시 함께 종료되지 않도록 함
        self.batch_manager = batch_manager  # 배치 관리자를 인스턴스 변수에 저장
        self.running: bool = False  # 스케줄러 실행 상태를 나타내는 변수 초기화
        self.login_service = login_service  # 로그인 서비스를 인스턴스 변수에 저장
        self.assignment_service = assignment_service  # 과제 서비스를 인스턴스 변수에 저장

        self.schedules = (  # 스케줄 목록 초기화
            WorkItem(  # 작업 항목 생성
                type=WorkType.REFRESH,  # 작업 유형을 REFRESH로 설정
                method=self.login_service.refresh,  # 실행할 메서드를 로그인 서비스의 refresh로 설정
                interval=3 * 60  # 실행 간격을 3분으로 설정
            ),
            WorkItem(  # 작업 항목 생성
                type=WorkType.COURSES,  # 작업 유형을 COURSES로 설정
                method=self.assignment_service.crawling_course,  # 실행할 메서드를 과제 서비스의 crawling_course로 설정
                interval=5  # 실행 간격을 5분으로 설정
            ),
            WorkItem(  # 작업 항목 생성
                type=WorkType.ASSIGNMENT,  # 작업 유형을 ASSIGNMENT로 설정
                method=self.assignment_service.crawling_assignments,  # 실행할 메서드를 과제 서비스의 crawling_assignments로 설정
                interval=5  # 실행 간격을 5분으로 설정
            ),
        )

    def run(self):  # 스레드 실행 메서드 정의
        """스케줄러 스레드 실행"""
        self.running = True  # 스케줄러 실행 상태를 True로 설정

        try:
            self._execute_work(  # 작업 실행 메서드 호출
                WorkItem(  # 작업 항목 생성
                    type=WorkType.LOGIN,  # 작업 유형을 LOGIN으로 설정
                    method=self.login_service.login,  # 실행할 메서드를 로그인 서비스의 login으로 설정
                    interval=0  # 실행 간격을 0으로 설정 (즉시 실행)
                )
            )

            # 정기 스케줄 등록
            for work_item in self.schedules:  # 스케줄 목록을 순회
                self._execute_work(work_item)  # 각 작업 항목에 대해 작업 실행
                schedule.every(work_item.interval).minutes.do(  # 주기적으로 작업 실행 등록
                    self._execute_work,  # 실행할 메서드
                    work_item  # 작업 항목
                )

            # 스케줄 실행
            while self.running:  # 스케줄러가 실행 중인 동안
                schedule.run_pending()  # 실행할 작업이 있는지 확인하고 실행
                time.sleep(1)  # 1초 대기
        except Exception as e:  # 예외 처리
            print(f"Scheduler error: {e}")  # 오류 메시지 출력

    def _execute_work(self, work_item: WorkItem):  # 작업 실행 메서드 정의
        """작업 실행"""
        try:
            self.batch_manager.process_work(work_item)  # 배치 관리자를 통해 작업 처리
        except Exception as e:  # 예외 처리
            print(f"Error executing {work_item.type.name}: {e}")  # 오류 메시지 출력

    def stop(self):  # 스케줄러 정지 메서드 정의
        """스케줄러 정지"""
        self.running = False  # 스케줄러 실행 상태를 False로 설정
        schedule.clear()  # 모든 스케줄을 초기화
