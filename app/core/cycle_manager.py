import asyncio
from datetime import datetime, timezone
import logging
from .event_type import EventType

logger = logging.getLogger(__name__)


class CycleManager:
    def __init__(self, stop_event: asyncio.Event, queue: asyncio.Queue, interval: int = 60):
        self.stop_event = stop_event
        self.queue = queue
        self.interval = interval
        self.counter = 0

    async def run(self):
        while not self.stop_event.is_set():
            if self.counter % self.interval == 0:
                payload = {
                    "type": f"{self.interval}_seconds",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                await self.queue.put((EventType.CYCLE, payload))
            await asyncio.sleep(1)
            self.counter += 1



