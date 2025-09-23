from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from models.log import Log
import logging

logger = logging.getLogger(__name__)


class Protocol:
    def __init__(self, websocket_manager, database_manager,  templates: Jinja2Templates):
        self.router = APIRouter(prefix="/protocol", tags=["protocol"])
        self.router.add_api_route("/", self.protocol, response_class=HTMLResponse, methods=["GET"])
        self.router.add_api_websocket_route("/ws", self.protocol_websocket)
        self.websocket_manager = websocket_manager
        self.database_manager = database_manager
        self.templates = templates

    async def protocol(self, request: Request):
        return self.templates.TemplateResponse("protocol.html", {"request": request})

    async def protocol_websocket(self, websocket: WebSocket):
        """
        WebSocket endpoint for real-time protocol updates
        """
        await self.websocket_manager.connect_protocol(websocket)

        try:
            # Send initial data (last 20 entries)
            with self.database_manager.session_scope() as db:
                initial_entries = db.query(Log).order_by(desc(Log.timestamp)).limit(20).all()
                initial_data = [entry.to_json() for entry in initial_entries]

                await self.websocket_manager.send_initial_protocol_data(websocket, initial_data)

            # Keep connection alive and handle client messages
            while True:
                try:
                    # Wait for client messages (e.g., ping/pong)
                    data = await websocket.receive_text()
                    logger.debug(f"Received protocol websocket message: {data}")
                except WebSocketDisconnect:
                    break

        except Exception as e:
            logger.error(f"Protocol WebSocket error: {e}")
        finally:
            self.websocket_manager.disconnect_protocol(websocket)
