from abc import ABC, abstractmethod
from core.event_type import EventType


class Plugin(ABC):

    _manager = None

    def set_manager(self, manager):
        self._manager = manager

    def can_handle(self, event_type: EventType) -> bool:
        if event_type == EventType.CYCLE:
            return True
        return False  # Default implementation, ignore all other Events

    @abstractmethod
    async def trigger(self, event_type: EventType, payload: dict):
        raise NotImplementedError("Trigger method must be implemented by subclasses")
