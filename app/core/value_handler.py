import logging
import asyncio

from pendulum import datetime, timezone

from .crud import create_or_update_value, read_current_values, read_value_or_null
from .event_handler import EventHandler
from .event_type import EventType
from .database_manager import DatabaseManager
from .websocket_manager import WebSocketManager

from models.value import Value


logger = logging.getLogger(__name__)


class ValueHandler(EventHandler):

    def __init__(self, queue: asyncio.Queue, database_manager: DatabaseManager, websocket_manager: WebSocketManager):
        self.queue = queue
        self.database_manager = database_manager
        self.websocket_manager = websocket_manager

    async def handle(self, event_type: EventType, payload: dict):

        if event_type != EventType.VALUE:
            return

        logger.info(f"New value entry: {payload}")
        new_value = Value.from_dict(payload)

        with self.database_manager.session_scope() as db:
            old_value = read_value_or_null(db, new_value.id)
            create_or_update_value(db, new_value)

            payload = {
                "id": new_value.id,
                "values": [new_value.to_json()]
            }
            if old_value is not None:
                payload["values"].append(old_value.to_json())

            # TODO validate and remove id from values
            for value in payload["values"]:
                assert value["id"] == payload["id"]
                del value["id"]
                
            await self.queue.put((EventType.VALUE_CHANGED, payload))

        with self.database_manager.session_scope() as db:
            latest_values = read_current_values(db)
            update_data = [value_entry.to_json() for value_entry in latest_values]
            await self.websocket_manager.broadcast_dashboard_values(update_data)
