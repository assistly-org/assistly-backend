from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from datetime import datetime
from typing import Dict, Any
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Store websocket -> client information
        self.active_connections: Dict[
            str,
            Dict[WebSocket, Dict[str, Any]]
        ] = {}

    async def connect(self,tenant_id: str, websocket: WebSocket) -> Dict[str, Any]:
        """
        Accept and register a websocket connection.
        """
        await websocket.accept()

        client = {
            "client_id": str(uuid.uuid4()),
            "connected_at": datetime.utcnow().isoformat(),
        }

        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = {}

        self.active_connections[tenant_id][websocket] = client

        logger.info(
            f"Client connected [{client['client_id']}]. "
            f"Active: {self.total_connections}"
        )

        return client

    def disconnect(self, tenant_id: str, websocket  : WebSocket) -> None:
        tenant_connections = self.active_connections.get(tenant_id)

        if tenant_connections:
            client = tenant_connections.pop(websocket, None)

            if not tenant_connections:
                self.active_connections.pop(tenant_id)

            if client:
                logger.info(
                    f"Client disconnected [{client['client_id']}]. "
                    f"Active: {self.total_connections}"
                )

    async def send_personal_message(
        self,
        tenant_id: str,
        websocket: WebSocket,
        message: Dict[str, Any],
    ) -> None:
        """
        Send a message to a single client.
        """
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(message)

        except Exception as e:
            logger.exception(f"Failed to send personal message: {e}")
            self.disconnect(tenant_id, websocket)

    async def broadcast(
        self,
        tenant_id: str,
        message: Dict[str, Any],
    ) -> None:
        """
        Send a message to all connected clients.
        """
        disconnected = []

        for websocket in list(self.active_connections.get(tenant_id, {}).keys()):
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message)

            except Exception as e:
                logger.exception(f"Broadcast failed: {e}")
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(tenant_id, websocket)

    @property
    def total_connections(self) -> int:
            return sum(
                len(connections)
                for connections in self.active_connections.values()
            )


manager = ConnectionManager()


@router.websocket("/ws/{tenant_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str,
):
    logger.info(f"Tenant connected: {tenant_id}")

    client = await manager.connect(tenant_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            logger.info(
                f"[{client['client_id']}] "
                f"Received: {data}"
            )

            message_type = data.get("type")

            if message_type == "chat":
                response = {
                    "type": "chat_response",
                    "tenant_id": tenant_id,
                    "message": f"Hello {data.get('message', '')}",
                    "client_id": client["client_id"],
                    "server_time": datetime.utcnow().isoformat(),
                }

            elif message_type == "ping":
                response = {
                    "type": "pong",
                    "tenant_id": tenant_id,
                    "server_time": datetime.utcnow().isoformat(),
                }

            elif message_type == "analytics":
                response = {
                    "type": "analytics",
                    "tenant_id": tenant_id,
                    "active_clients": manager.total_connections,
                    "server_time": datetime.utcnow().isoformat(),
                }

            else:
                response = {
                    "type": "error",
                    "message": "Unknown message type",
                    "server_time": datetime.utcnow().isoformat(),
                }

            await manager.send_personal_message(
                tenant_id,
                websocket,
                response,
            )

    except WebSocketDisconnect:
        logger.info(
            f"[{client['client_id']}] WebSocket disconnected."
        )

    except Exception as e:
        logger.exception(
            f"[{client['client_id']}] Unexpected error: {e}"
        )

    finally:
        manager.disconnect(tenant_id, websocket)