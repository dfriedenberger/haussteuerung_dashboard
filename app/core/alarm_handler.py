import logging

from .crud import create_or_update_alarm, read_alarms, update_alarm_acknowledged
from .event_handler import EventHandler
from .event_type import EventType
from .database_manager import DatabaseManager
from .websocket_manager import WebSocketManager


from models.alarm import Alarm


logger = logging.getLogger(__name__)


class AlarmHandler(EventHandler):

    def __init__(self, database_manager: DatabaseManager, websocket_manager: WebSocketManager):
        self.database_manager = database_manager
        self.websocket_manager = websocket_manager

    async def handle(self, event_type: EventType, payload: dict):

        update = False
        if event_type == EventType.ALARM:
            new_alarm = Alarm.from_dict(payload)
            with self.database_manager.session_scope() as db:
                create_or_update_alarm(db, new_alarm)
                update = True

        if event_type == EventType.ALARM_ACKNOWLEDGE:
            alarm_id = payload.get("alarm_id")
            logger.info(f"Acknowledging alarm with ID: {alarm_id}")
            with self.database_manager.session_scope() as db:
                update_alarm_acknowledged(db, alarm_id)
                update = True

        if update:  # broadcast update if there was a change
            with self.database_manager.session_scope() as db:
                update_alarms = read_alarms(db)
                update_data = [alarm.to_json() for alarm in update_alarms]
                await self.websocket_manager.broadcast_alarm_update(update_data)
