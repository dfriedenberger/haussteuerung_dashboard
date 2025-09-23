import queue
from typing import List
import logging

from core.event_type import EventType
from .plugin import Plugin
from .meross import Meross
from .simulator import Simulator

logger = logging.getLogger(__name__)


class PluginManager:

    def __init__(self, queue: queue.Queue):
        self.plugins: List[Plugin] = []
        self.queue = queue
        
    def load(self):
        self.plugins.append(Meross())
        self.plugins.append(Simulator())

        for plugin in self.plugins:
            plugin.set_manager(self)

    def trigger(self, event_type, payload):
        for plugin in self.plugins:
            try:
                plugin.trigger(event_type, payload)
            except Exception as e:
                logger.error(f"Plugin raised Exception {e}")

    def put_event(self, event_type: EventType, payload: dict):
        """Thread-safe method to put events into the queue"""
        try:
            self.queue.put((event_type, payload), timeout=1)
        except queue.Full:
            logger.warning(f"Could not queue event {event_type} - queue full")
