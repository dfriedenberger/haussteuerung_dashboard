import logging
from datetime import datetime, timezone

from sqlalchemy import values

from core.event_type import EventType
from .plugin import Plugin


logger = logging.getLogger(__name__)


class Simulator(Plugin):

    def can_handle(self, event_type: EventType) -> bool:
        if event_type in [EventType.CYCLE, EventType.VALUE_CHANGED]:
            return True
        return False

    async def trigger(self, event_type: EventType, payload: dict):
        logger.info(f"Simulator plugin triggered with {event_type} and payload: {payload}")

        if event_type == EventType.CYCLE:
            await self.simulate_value()
        
        if event_type == EventType.VALUE_CHANGED:
            await self.handle_value_changed(payload)
           

    async def log_info(self, message: str):
        log_payload = {
            "message": message,
            "protocol": "plugin_simulator",
            "level": "INFO",
            "ref_id": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self._manager.put_event(EventType.LOG, log_payload)

    _cnt = 0

    async def simulate_value(self):
        self._cnt += 1
        simulated_value = (self._cnt + 18) % 20 * 0.1 + 20  # cycles between 20.0 and 22.0
        await self.log_info(f"Simulate temperature sensor data {simulated_value:.1f}°C")
        value_payload = {
            "id": "simulated_device_1",
            "value_type": "temperature",
            "value": f"{simulated_value:.1f}",
            "unit": "°C",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await self._manager.put_event(EventType.VALUE, value_payload)

    async def handle_value_changed(self, payload: dict):

        if payload.get("id") != "simulated_device_1":
            return  # only handle our simulated device

        values = []
        active = []
        for value_entry in payload.get("values", []):
            simulated_value = float(value_entry.get("value"))
            value_active = simulated_value > 21.0  # Alarm if temperature > 21.0°C
            values.append(simulated_value)
            active.append(value_active)

        if len(values) == 1:
            values.append(None)  # ensure we have two entries for comparison
            active.append(False)

        if active[0] is not active[1]:  # changed state
            # raise alarm
            alarm_payload = {
                "active": active[0],
                "acknowledged": False,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Alarm: {active[0]} Temperature changed from {values[1]} to {values[0]} °C",
                "alarm_type": "TemperatureThreshold",
                "device_id": "simulated_device_1",
                "priority": 2  # Medium priority
            }
            await self._manager.put_event(EventType.ALARM, alarm_payload)
