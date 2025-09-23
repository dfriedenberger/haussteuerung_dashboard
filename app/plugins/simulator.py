import logging
from datetime import datetime, timezone

from core.event_type import EventType
from .plugin import Plugin


logger = logging.getLogger(__name__)


class Simulator(Plugin):

    _simulated_value = 22.1

    def trigger(self, event_type: EventType, payload: dict):
        logger.info(f"Simulator plugin triggered with {event_type} and payload: {payload}")

        if event_type == EventType.CYCLE:
            # Simulate a protocol entry event
            log_payload = {
                "message": "Simulated log entry",
                "protocol": "SIM",
                "level": "INFO",
                "ref_id": None,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._manager.put_event(EventType.LOG, log_payload)

            # Simulate a value entry event
            value_payload = {
                "id": "simulated_device_1",
                "value_type": "temperature",
                "value": f"{self._simulated_value:.1f}",
                "unit": "°C",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._manager.put_event(EventType.VALUE, value_payload)

            # Update simulated value for next cycle
            self._simulated_value += 0.1
