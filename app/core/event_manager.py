import asyncio
import logging
from typing import List, Dict
from .event_handler import EventHandler

from core.event_type import EventType
from plugins.plugin_manager import PluginManager

logger = logging.getLogger(__name__)


class EventManager:
    def __init__(
        self,
        stop_event: asyncio.Event,
        queue: asyncio.Queue,
        plugin_manager: PluginManager
    ):
        self.stop_event = stop_event
        self.event_queue = queue
        self.plugin_manager = plugin_manager
        self.event_handlers: Dict[EventType, List[EventHandler]] = {}

    def register_event_handler(self, event_types: List[EventType], handler: EventHandler):
        for event_type in event_types:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(handler)

    async def handle_event(self, event_type: EventType, payload: dict):
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                await handler.handle(event_type, payload)

    async def run(self):
        while not self.stop_event.is_set():
            try:
                # Timeout, damit wir regelmäßig stop_event prüfen
                event, payload = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            logger.info(f"Event: {event}, Payload: {payload}")
            await self.handle_event(event, payload)

            # redirect to Plugins (synchron)
            await self.plugin_manager.trigger(event, payload)

            self.event_queue.task_done()
