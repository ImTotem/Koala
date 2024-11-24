from koala.domain.assignment.model import BaseAssignment


# TODO : DTO 작성하기
class AssignmentDTO:

    def __init__(self):
        ...

    @classmethod
    def factory(cls, assignment: BaseAssignment):
        # TODO : 시간 보정
        cls()
