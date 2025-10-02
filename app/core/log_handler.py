import logging

from .crud import create_log
from .event_handler import EventHandler
from .event_type import EventType
from .database_manager import DatabaseManager
from .websocket_manager import WebSocketManager

from models.log import Log


logger = logging.getLogger(__name__)


class LogHandler(EventHandler):

    def __init__(self, database_manager: DatabaseManager, websocket_manager: WebSocketManager):
        self.database_manager = database_manager
        self.websocket_manager = websocket_manager

    async def handle(self, event_type: EventType, payload: dict):

        if event_type != EventType.LOG:
            return

        logger.info(f"New log entry: {payload}")
        new_log = Log.from_dict(payload)
        with self.database_manager.session_scope() as db:
            create_log(db, new_log)
            await self.websocket_manager.broadcast_protocol_entry(new_log.to_json())
