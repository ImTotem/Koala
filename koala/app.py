"""프로그램 시작점

진입점을 통해 시작되는 메인 부분
"""
import time  # 시간 관련 기능을 사용하기 위한 모듈 임포트
from multiprocessing import Queue, Process  # 멀티프로세싱을 위한 Queue와 Process 클래스 임포트

from dependency_injector import providers  # 의존성 주입을 위한 providers 임포트

from koala.batch.core.result_collector import ResultCollector  # 결과 수집기를 위한 클래스 임포트
from koala.di import DI  # 의존성 주입을 위한 DI 클래스 임포트
from koala.domain.view.gui import gui_main  # GUI 메인 함수 임포트


# 배치 프로세스를 실행하는 함수
def run_worker_process(queue: Queue):
    di = DI()  # DI 인스턴스 생성
    di.wire(packages=['koala'])  # 'koala' 패키지에 대한 의존성 주입 설정
    di.init_resources()  # 리소스 초기화

    # 결과 수집기를 스레드 안전한 싱글톤으로 오버라이드
    di.result_collector.override(providers.ThreadSafeSingleton(
        ResultCollector,
        courses=di.assignment.courses,  # 과목 정보 전달
        queue=queue  # 큐 전달
    ))

    di.worker_pool().start()  # 작업자 풀 시작

    di.result_collector().attach(di.batch_manager())  # 결과 수집기를 배치 관리자에 연결

    scheduler = di.scheduler()  # 스케줄러 인스턴스 생성
    scheduler.start()  # 스케줄러 시작

    try:
        while True:  # 무한 루프
            time.sleep(1)  # 1초 대기
    except KeyboardInterrupt:  # 키보드 인터럽트 발생 시
        scheduler.stop()  # 스케줄러 중지


# GUI 프로세스를 실행하는 함수
def run_gui_process(queue: Queue):
    di = DI()  # DI 인스턴스 생성
    di.wire(packages=['koala'])  # 'koala' 패키지에 대한 의존성 주입 설정
    di.init_resources()  # 리소스 초기화

    gui_main(queue)  # GUI 메인 함수 호출


# 프로그램 실행 함수
def run() -> None:
    ipc_queue = Queue()  # IPC 큐 생성

    # 작업자 프로세스와 GUI 프로세스 생성
    worker_process = Process(target=run_worker_process, args=(ipc_queue,))
    gui_process = Process(target=run_gui_process, args=(ipc_queue,))

    worker_process.start()  # 작업자 프로세스 시작
    gui_process.start()  # GUI 프로세스 시작

    try:
        gui_process.join()  # GUI 프로세스가 종료될 때까지 대기
    finally:
        worker_process.terminate()  # 작업자 프로세스 종료
        worker_process.join()  # 작업자 프로세스가 종료될 때까지 대기
