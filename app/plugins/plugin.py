from abc import ABC, abstractmethod
from core.event_type import EventType


class Plugin(ABC):

    _manager = None

    def set_manager(self, manager):
        self._manager = manager

    @abstractmethod
    def trigger(self, event_type: EventType, payload: dict):
        raise NotImplementedError("Trigger method must be implemented by subclasses")
