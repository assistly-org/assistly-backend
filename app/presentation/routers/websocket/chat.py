from fastapi import APIRouter, WebSocket, WebSocketDisconnect

print("🔥 WebSocket router loaded")
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()

            await websocket.send_text(
                f"Received: {data}"
            )

    except WebSocketDisconnect:
        print("Client disconnected")