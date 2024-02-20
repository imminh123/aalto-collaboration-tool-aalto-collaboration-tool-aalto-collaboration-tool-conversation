
# from fastapi import FastAPI, WebSocket
# from fastapi.responses import HTMLResponse
# import json

# app = FastAPI()

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         message = await websocket.receive_text()
#         # print(data)
#         messages = ["Sender_id", "Channel_id", message]
#         await websocket.send_text(json.dumps(messages))


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket = None):
        for connection in self.active_connections:
            if connection != websocket:
                await connection.send_text(message)

    async def send_direct_message(self, message: str, websocket: WebSocket = None):
        pass

    async def send_channel_message(self,message:str, websocket: WebSocket = None):
        pass

    async def send_edit_file_message(self,message:str, websocket: WebSocket = None):
        pass


manager = ConnectionManager()



@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(data, websocket)
            await manager.broadcast(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")