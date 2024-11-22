"""옵저버 패턴

https://refactoring.guru/ko/design-patterns/observer
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """
        Receive update from subject.
        """
        pass


class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        """
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        """
        self._observers.remove(observer)

    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        for observer in self._observers:
            observer.update(self)


__all__ = (
    'Observer',
    'Subject',
)
