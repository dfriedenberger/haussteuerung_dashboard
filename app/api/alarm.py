from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from models.alarm import Alarm
import logging
import json
import asyncio
from core.event_type import EventType

logger = logging.getLogger(__name__)


class AlarmApi:
    def __init__(self, websocket_manager, database_manager, event_queue: asyncio.Queue, templates: Jinja2Templates):
        self.router = APIRouter(prefix="/alarm", tags=["alarm"])
        self.router.add_api_route("/", self.alarm, response_class=HTMLResponse, methods=["GET"])
        self.router.add_api_websocket_route("/ws", self.alarm_websocket)
        self.websocket_manager = websocket_manager
        self.database_manager = database_manager
        self.event_queue = event_queue
        self.templates = templates

    async def alarm(self, request: Request):
        return self.templates.TemplateResponse("alarm.html", {"request": request})

    async def alarm_websocket(self, websocket: WebSocket):
        """
        WebSocket endpoint for real-time alarm updates
        """
        await self.websocket_manager.connect_alarm(websocket)

        try:
            # Send initial data (all alarms sorted by priority and timestamp)
            with self.database_manager.session_scope() as db:
                initial_alarms = (db.query(Alarm)
                                  .order_by(desc(Alarm.priority), desc(Alarm.timestamp))
                                  .limit(100)
                                  .all())
                initial_data = [alarm.to_json() for alarm in initial_alarms]

                await self.websocket_manager.send_initial_alarm_data(websocket, initial_data)

            # Keep connection alive and handle client messages
            while True:
                try:
                    # Wait for client messages (e.g., ping/pong)
                    data = await websocket.receive_text()
                    logger.info(f"Received alarm websocket message: {data}")
                    # TODO: Validate Message
                    # {"type":"acknowledge_alarm","data":{"alarm_id":6}}
                    message = json.loads(data)
                    if message.get("type") == "acknowledge_alarm":
                        alarm_id = message["data"]["alarm_id"]
                        payload = {"command_type": "acknowledge_alarm", "alarm_id": alarm_id}
                        await self.event_queue.put((EventType.COMMAND, payload))

                except WebSocketDisconnect:
                    break

        except Exception as e:
            logger.error(f"Alarm WebSocket error: {e}")
        finally:
            self.websocket_manager.disconnect_alarm(websocket)