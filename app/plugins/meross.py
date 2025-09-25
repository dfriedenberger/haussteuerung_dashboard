import logging

from core.event_type import EventType
from .plugin import Plugin


logger = logging.getLogger(__name__)


class Meross(Plugin):

    async def trigger(self, event_type: EventType, payload: dict):
        logger.info(f"Meross plugin triggered with {event_type} and payload: {payload}")

