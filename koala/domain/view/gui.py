from dependency_injector.wiring import inject, Provide

from koala.di import DI
from koala.domain.assignment.controller import AssignmentController
from koala.utils import Observer, Subject


class GUI(Observer):

    def __init__(self, controller: AssignmentController):
        self._controller = controller

    def update(self, subject: Subject) -> None:
        self.update_ui()

    def update_ui(self) -> None:
        print(self._controller.get_assignments())


@inject
def gui_main(controller: AssignmentController = Provide[DI.assignment.controller]):
    gui = GUI(controller)
    controller.attach(gui)
    while True:
        ...
