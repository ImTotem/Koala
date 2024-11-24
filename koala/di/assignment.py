"""과제 수집 관련 의존성 컨테이너 모듈"""

from dependency_injector import containers, providers

from koala.domain.assignment.controller import AssignmentController
from koala.domain.assignment.model import Course
from koala.domain.assignment.service import AssignmentService


class _AssignmentContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    cookies = providers.Dependency()

    courses = providers.ThreadSafeSingleton(
        set[Course]
    )

    service = providers.ThreadSafeSingleton(
        AssignmentService,
        cookies=cookies,
        courses=courses,
    )

    controller = providers.ThreadSafeSingleton(
        AssignmentController,
        service=service,
    )


__all__ = (
    '_AssignmentContainer',
)
