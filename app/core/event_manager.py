import asyncio
import logging

from core.crud import get_current_values
from core.websocket_manager import WebSocketManager 
from core.database_manager import DatabaseManager
from core.event_type import EventType
from plugins.plugin_manager import PluginManager    
from models.log import Log
from models.value import Value

logger = logging.getLogger(__name__)


class EventManager:
    def __init__(
        self,
        stop_event: asyncio.Event,
        queue: asyncio.Queue,
        websocket_manager: WebSocketManager,
        database_manager: DatabaseManager,
        plugin_manager: PluginManager
    ):
        self.stop_event = stop_event
        self.event_queue = queue
        self.websocket_manager = websocket_manager
        self.database_manager = database_manager
        self.plugin_manager = plugin_manager

    async def run(self):
        while not self.stop_event.is_set():
            try:
                # Timeout, damit wir regelmäßig stop_event prüfen
                event, payload = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            logger.info(f"Event: {event}, Payload: {payload}")

            # Handle event: store in DB, send via WebSocket, etc.
            if event == EventType.LOG:
                new_log = Log.from_dict(payload)
                with self.database_manager.session_scope() as db:
                    db.add(new_log)
                    await self.websocket_manager.broadcast_protocol_entry(new_log.to_json())

            elif event == EventType.VALUE:
                new_value = Value.from_dict(payload)
                logger.info(f"Storing new value: {new_value.to_json()}")
                with self.database_manager.session_scope() as db:
                    exists = db.query(Value).filter_by(id=new_value.id, timestamp=new_value.timestamp).first()
                    if exists:
                        logger.info(f"Value with id {new_value.id} and timestamp {new_value.timestamp} already exists. Skip insert")
                    else:
                        db.add(new_value)
              
                with self.database_manager.session_scope() as db:
                    latest_values = get_current_values(db)
                    update_data = [value_entry.to_json() for value_entry in latest_values]
                    await self.websocket_manager.broadcast_dashboard_values(update_data)

            # redirect to Plugins (synchron)
            await self.plugin_manager.trigger(event, payload)

            self.event_queue.task_done()

