"""프로그램 시작점

진입점을 통해 시작되는 메인 부분
"""
import time
from multiprocessing import Queue, Process

from dependency_injector import providers

from koala.batch.core.result_collector import ResultCollector
from koala.di import DI
from koala.domain.view.gui import gui_main


def run_worker_process(queue: Queue):
    di = DI()
    di.wire(packages=['koala'])
    di.init_resources()

    di.result_collector.override(providers.ThreadSafeSingleton(
        ResultCollector,
        courses=di.assignment.courses,
        queue=queue
    ))

    di.worker_pool().start()

    di.result_collector().attach(di.batch_manager())

    scheduler = di.scheduler()
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()


def run_gui_process(queue: Queue):
    di = DI()
    di.wire(packages=['koala'])
    di.init_resources()

    gui_main(queue)


def run() -> None:
    ipc_queue = Queue()

    worker_process = Process(target=run_worker_process, args=(ipc_queue,))
    gui_process = Process(target=run_gui_process, args=(ipc_queue,))

    worker_process.start()
    gui_process.start()

    try:
        gui_process.join()
    finally:
        worker_process.terminate()
        worker_process.join()
