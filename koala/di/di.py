"""의존성 주입 컨테이너 모듈
전체 애플리케이션의 의존성을 관리하는 메인 컨테이너
"""
from multiprocessing import Queue  # 멀티프로세싱을 위한 Queue 클래스를 임포트

from dependency_injector import containers, providers  # 의존성 주입을 위한 containers와 providers를 임포트

from koala.batch.core.batch_manager import BatchManager  # 배치 작업을 관리하는 BatchManager 클래스를 임포트
from koala.batch.core.result_collector import ResultCollector  # 작업 결과를 수집하는 ResultCollector 클래스를 임포트
from koala.batch.core.worker_pool import WorkerPool  # 작업자 풀을 관리하는 WorkerPool 클래스를 임포트
from koala.batch.scheduler.scheduler import Scheduler  # 스케줄링 작업을 수행하는 Scheduler 클래스를 임포트
from koala.conf.config import ConfigContainer  # 설정을 관리하는 ConfigContainer 클래스를 임포트
from koala.di.assignment import _AssignmentContainer  # 과제 관련 의존성을 관리하는 _AssignmentContainer 클래스를 임포트
from koala.di.auth import _AuthContainer  # 인증 관련 의존성을 관리하는 _AuthContainer 클래스를 임포트

class DI(containers.DeclarativeContainer):
    """메인 의존성 주입 컨테이너.
    
    :ivar config: 설정 컨테이너
    :type config: providers.Container
    :ivar auth: 인증 관련 컨테이너
    :type auth: providers.Container
    :ivar schedule_manager: 스케줄 관리자 싱글톤
    :type schedule_manager: providers.ThreadSafeSingleton
    """
    
    config = providers.Container(ConfigContainer).config  # ConfigContainer에서 설정을 가져옴 config 변수에 할당

    auth = providers.Container(  # 인증 관련 의존성 컨테이너를 정의
        _AuthContainer,  # _AuthContainer 클래스를 사용
        config=config,  # 위에서 정의한 config를 전달
    )

    assignment = providers.Container(  # 과제 관련 의존성 컨테이너를 정의
        _AssignmentContainer,  # _AssignmentContainer 클래스를 사용
        config=config,  # 위에서 정의한 config를 전달
        cookies=auth.cookies,  # 인증 쿠키를 auth에서 가져와 전달
    )

    result_collector = providers.ThreadSafeSingleton(  # 결과 수집기를 위한 스레드 안전한 싱글톤을 정의
        ResultCollector,  # ResultCollector 클래스를 사용
        courses=assignment.courses,  # 과목 정보를 assignment에서 가져와 전달
        queue=None,  # 큐는 None으로 초기화
    )

    worker_pool = providers.ThreadSafeSingleton(  # 작업자 풀을 위한 스레드 안전한 싱글톤을 정의
        WorkerPool,  # WorkerPool 클래스를 사용
        result_collector=result_collector,  # 결과 수집기를 전달
    )

    batch_manager = providers.ThreadSafeSingleton(  # 배치 관리자를 위한 스레드 안전한 싱글톤을 정의
        BatchManager,  # BatchManager 클래스를 사용
        worker_pool=worker_pool,  # 작업자 풀을 전달
        courses=assignment.courses  # 과목 정보를 assignment에서 가져와 전달
    )

    scheduler = providers.ThreadSafeSingleton(  # 스케줄러를 위한 스레드 안전한 싱글톤을 정의
        Scheduler,  # Scheduler 클래스를 사용
        batch_manager=batch_manager,  # 배치 관리자를 전달
        login_service=auth.service,  # 로그인 서비스를 auth에서 가져와 전달
        assignment_service=assignment.service,  # 과제 서비스를 assignment에서 가져와 전달
    )

__all__ = (  # 모듈에서 공개할 객체 목록을 정의
    'DI',  # DI 클래스를 공개
)
