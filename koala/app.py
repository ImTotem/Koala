import asyncio

from koala.di import DI


def run() -> None:
    container = DI()
    container.wire(packages=['koala'])

    asyncio.run(container.auth.service().login())
