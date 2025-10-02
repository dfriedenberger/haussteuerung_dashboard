from .event_type import EventType
from abc import ABC, abstractmethod


class EventHandler(ABC):

    @abstractmethod
    async def handle(self, event_type: EventType, payload: dict):
        raise NotImplementedError("Subclasses must implement this method.")
