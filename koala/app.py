import asyncio

from koala.di import DI
from koala.domain.view.gui import gui_main


def run() -> None:
    di = DI()
    di.wire(packages=['koala'])

    di.init_resources()
    asyncio.run(di.schedule_manager().start())

    gui_main()
