from typing import List

from koala.domain.assignment.dto import AssignmentDTO
from koala.domain.assignment.service import AssignmentService
from koala.utils import Observer


class AssignmentController:
    def __init__(self, service: AssignmentService):
        self._service = service

    def get_assignments(self) -> List[AssignmentDTO]:
        return list(map(
            lambda assignment: AssignmentDTO.factory(assignment),
            self._service.get_assignments()
        ))

    def attach(self, observer: Observer):
        self._service.attach(observer)

    def detach(self, observer: Observer):
        self._service.detach(observer)


__all__ = (
    'AssignmentController',
)
