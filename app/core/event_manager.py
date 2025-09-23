import asyncio
import queue
import threading
import logging

from core.crud import get_current_values
from core.websocket_manager import WebSocketManager 
from core.database_manager import DatabaseManager
from core.event_type import EventType
from plugins.plugin_manager import PluginManager    
from models.log import Log
from models.value import Value


logger = logging.getLogger(__name__)


class EventManager(threading.Thread):
    def __init__(self, stop_event: threading.Event, queue: queue.Queue, websocket_manager: WebSocketManager,
                 database_manager: DatabaseManager, plugin_manager: PluginManager):
        super().__init__()
        self.stop_event = stop_event
        self.event_queue = queue
        self.websocket_manager = websocket_manager
        self.database_manager = database_manager
        self.plugin_manager = plugin_manager

    def run(self):

        while not self.stop_event.is_set():
            try:
                event, payload = self.event_queue.get(timeout=1)
                logger.info(f"Event: {event}, Payload: {payload}")

                # Handle event: store in DB, send via WebSocket, etc.
                if event == EventType.LOG:
                    new_log = Log.from_dict(payload)
                    with self.database_manager.session_scope() as db:
                        db.add(new_log)
                        asyncio.run(self.websocket_manager.broadcast_protocol_entry(new_log.to_json()))

                if event == EventType.VALUE:
                    new_value = Value.from_dict(payload)
                    with self.database_manager.session_scope() as db:
                        db.add(new_value)
                    with self.database_manager.session_scope() as db:
                        latest_values = get_current_values(db)
                        update_data = [value_entry.to_json() for value_entry in latest_values]
                        asyncio.run(self.websocket_manager.broadcast_dashboard_values(update_data))

                # redirect to Plugins
                self.plugin_manager.trigger(event, payload)

                self.event_queue.task_done()
            except queue.Empty:
                continue
