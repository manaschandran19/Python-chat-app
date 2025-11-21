from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import json
from starlette.websockets import WebSocketDisconnect
import logging

# Configure basic logging for the app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager:
    """Manage connections mapped by username for private messaging."""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket
        logger.info("WebSocket connection accepted; total=%d", len(self.active_connections))

    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]
        logger.info("WebSocket disconnected; total=%d", len(self.active_connections))

    async def send_personal_message(self, message: str, username: str):
        ws = self.active_connections.get(username)
        if ws:
            await ws.send_text(message)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections.values()):
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(username, websocket)
    logger.info("Client %s connected", username)
    try:
        while True:
            text = await websocket.receive_text()
            # expect JSON: {"to": "recipient", "message": "..."}
            try:
                payload = json.loads(text)
                to_user = payload.get("to")
                message = payload.get("message", "")
            except Exception:
                # fallback: treat entire text as broadcast message
                to_user = None
                message = text

            if to_user:
                # private message
                logger.info("Private from %s to %s: %s", username, to_user, message)
                await manager.send_personal_message(f"(private) {username}: {message}", to_user)
                # echo to sender for confirmation
                await manager.send_personal_message(f"(to {to_user}) You: {message}", username)
            else:
                # broadcast
                logger.info("Broadcast from %s: %s", username, message)
                await manager.broadcast(f"{username}: {message}")
    except WebSocketDisconnect:
        logger.info("Client %s disconnected (WebSocketDisconnect)", username)
    except Exception as e:
        logger.exception("WebSocket error for client %s: %s", username, e)
    finally:
        manager.disconnect(username)
        await manager.broadcast(f"{username} left the chat")
        logger.info("Client %s cleanup complete", username)
