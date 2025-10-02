from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import logging

from core.crud import read_current_values

logger = logging.getLogger(__name__)


class Dashboard:
    def __init__(self, websocket_manager, database_manager, templates: Jinja2Templates):
        self.router = APIRouter(prefix="/dashboard", tags=["dashboard"])
        self.router.add_api_route("/", self.dashboard, response_class=HTMLResponse, methods=["GET"])
        self.router.add_api_websocket_route("/ws", self.dashboard_websocket)
        self.websocket_manager = websocket_manager
        self.database_manager = database_manager
        self.templates = templates

    async def dashboard(self, request: Request):
        return self.templates.TemplateResponse("dashboard.html", {"request": request})

    async def dashboard_websocket(self, websocket: WebSocket):
        """
        WebSocket endpoint for real-time dashboard updates
        """
        await self.websocket_manager.connect_dashboard(websocket)

        try:
            # Send initial data
            with self.database_manager.session_scope() as db:
                latest_values = read_current_values(db)
                initial_data = [value_entry.to_json() for value_entry in latest_values]
                await self.websocket_manager.send_initial_dashboard_data(websocket, initial_data)

            # Keep connection alive and handle client messages
            while True:
                try:
                    # Wait for client messages (e.g., ping/pong)
                    data = await websocket.receive_text()
                    logger.debug(f"Received dashboard websocket message: {data}")
                except WebSocketDisconnect:
                    break

        except Exception as e:
            logger.error(f"Dashboard WebSocket error: {e}")
        finally:
            self.websocket_manager.disconnect_dashboard(websocket)
