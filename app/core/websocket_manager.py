from typing import List, Dict
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        # Separate connections for different types
        self.protocol_connections: List[WebSocket] = []
        self.dashboard_connections: List[WebSocket] = []

    async def connect_protocol(self, websocket: WebSocket):
        """Connect a websocket for protocol updates"""
        await websocket.accept()
        self.protocol_connections.append(websocket)
        logger.info(f"Protocol WebSocket connected. Total connections: {len(self.protocol_connections)}")

    async def connect_dashboard(self, websocket: WebSocket):
        """Connect a websocket for dashboard updates"""
        await websocket.accept()
        self.dashboard_connections.append(websocket)
        logger.info(f"Dashboard WebSocket connected. Total connections: {len(self.dashboard_connections)}")

    def disconnect_protocol(self, websocket: WebSocket):
        """Disconnect a protocol websocket"""
        if websocket in self.protocol_connections:
            self.protocol_connections.remove(websocket)
            logger.info(f"Protocol WebSocket disconnected. Remaining connections: {len(self.protocol_connections)}")

    def disconnect_dashboard(self, websocket: WebSocket):
        """Disconnect a dashboard websocket"""
        if websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)
            logger.info(f"Dashboard WebSocket disconnected. Remaining connections: {len(self.dashboard_connections)}")

    async def broadcast_protocol_entry(self, log_entry: Dict):
        """Broadcast a new protocol entry to all connected protocol clients"""
        if not self.protocol_connections:
            return

        message = {
            "type": "new_entry",
            "data": log_entry
        }

        # Send to all connections, remove broken ones
        disconnected = []
        for connection in self.protocol_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending protocol message: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect_protocol(conn)

    async def broadcast_dashboard_values(self, values_data: List[Dict]):
        """Broadcast updated dashboard values to all connected dashboard clients"""
        if not self.dashboard_connections:
            return

        message = {
            "type": "values_update",
            "data": values_data
        }

        # Send to all connections, remove broken ones
        disconnected = []
        for connection in self.dashboard_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending dashboard message: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect_dashboard(conn)

    async def send_initial_protocol_data(self, websocket: WebSocket, entries: List[Dict]):
        """Send initial protocol data to a newly connected client"""
        message = {
            "type": "initial_data",
            "data": {"entries": entries}
        }
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending initial protocol data: {e}")

    async def send_initial_dashboard_data(self, websocket: WebSocket, values_data: Dict):
        """Send initial dashboard data to a newly connected client"""
        message = {
            "type": "initial_data",
            "data": values_data
        }
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending initial dashboard data: {e}")



