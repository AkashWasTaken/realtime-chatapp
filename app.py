from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict
import uvicorn

app = FastAPI()

# Store connected clients and their usernames
connected_clients: List[WebSocket] = []
usernames: Dict[WebSocket, str] = {}

@app.get("/")
async def get():
    with open("index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Add the new client
    connected_clients.append(websocket)
    username = await websocket.receive_text()  # Receive the username
    usernames[websocket] = username
    await broadcast(f"{username} has joined the chat!")

    try:
        while True:
            data = await websocket.receive_text()  # Receive a message
            await broadcast(f"{username}: {data}")  # Broadcast message
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        del usernames[websocket]
        await broadcast(f"{username} has left the chat!")

async def broadcast(message: str):
    for client in connected_clients:
        await client.send_text(message)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
