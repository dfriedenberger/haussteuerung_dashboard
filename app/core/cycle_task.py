import queue
import threading
import time
import logging
from .event_type import EventType
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class CycleTask(threading.Thread):
    def __init__(self, stop_event: threading.Event, queue: queue.Queue):
        super().__init__()
        self.stop_event = stop_event
        self.queue = queue

    def run(self):
        counter = 0
        while not self.stop_event.is_set():
            if counter % 60 == 0:
                if counter % 60 == 0:
                    # Trigger cycle event
                    payload = {
                        "type": "60_seconds",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    self.queue.put((EventType.CYCLE, payload))
            time.sleep(1)
            counter += 1
