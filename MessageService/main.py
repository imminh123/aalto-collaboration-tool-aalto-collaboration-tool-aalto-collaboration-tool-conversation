from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import json
import uuid


app = FastAPI()

# app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost"])

messagesHistory = []
onlineUserList = []
channelList = [
    {"channelId": str(uuid.uuid4()),
     "channelName": "General", 
     "channelType": "public",
     "channelMembers": []},
    {"channelId": str(uuid.uuid4()),
     "channelName": "Important", 
     "channelType": "public",
     "channelMembers": []},
    {"channelId": str(uuid.uuid4()),
     "channelName": "Random",
     "channelType": "public",
     "channelMembers": []},
]

class ConnectionManager:
    def __init__(self):
        # self.active_connections: list[WebSocket] = []
        self.active_connections = {}

    def __len__(self):
        return len(self.active_connections)

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, websocket: WebSocket, client_id: str):
        removedConnection = self.active_connections.get(client_id, None)
        if(removedConnection != None):
            del self.active_connections[client_id]

    async def broadcast(self, message: str, websocket: WebSocket = None):
        for key, value in self.active_connections.items():
            await value.send_text(message)

    async def user_status_boardcast(self, userId: str):
        broadcastMessage = {
            "loginType": 0,
            "onlineUserList": onlineUserList
        }
        newConnection = self.active_connections.get(userId, None)
        if(newConnection != None):
            await newConnection.send_json({
                "messagesHistory":messagesHistory,
                "channelHistory":channelList,
                "loginType": 1 
                })
        for key,value in self.active_connections.items():
            await value.send_json(broadcastMessage)

    async def send_personal_message(self, data: str, receiverId: str, receiverName:str, senderId: str, senderName: str, websocket: WebSocket):
        for key, value in self.active_connections.items():
            if key == receiverId:
                await value.send_text(data)
            if key == senderId:
                await value.send_text(data)

    async def send_channel_message(self, data: str):
        # Broad cast to all the users, can be filter to users in the channel only in future
        for key, value in self.active_connections.items():
            await value.send_text(data)

    async def send_edit_file(self, userId: str, fileId: str, content: str):
        # Broad cast
        for key, value in self.active_connections.items():
            await value.send_json({
                "fileContent":content,
                "fileId":fileId,
                "senderId":userId,
            })

    
    async def send_file_user(self, file: str, channel: str):
        pass

    async def send_file_channel(self, file: bytes=None, channel: str=""):
        for key, value in self.active_connections.items():
            await value.send_bytes(file)

    async def create_new_channel(self, jsonObject):
        channelList.append(jsonObject['newChannel'])
        for key, value in self.active_connections.items():
            userChannelList = []
            for channel in channelList:
                if key in channel['channelMembers'] or channel['channelType'] == "public":
                    userChannelList.append(channel)
            if (key in jsonObject['newChannel']['channelMembers']):
                await value.send_json({
                    "channelHistory":userChannelList,
                    "loginType": 2
                })

    async def delete_channel(self, jsonObject, channelId: str, websocket: WebSocket):
        updatedUsersList = [x for x in channelList if x['channelId'] == channelId]
        if len(updatedUsersList) != 0:
            if(updatedUsersList[0]['channelType'] == "public"):
                return
            updatedUsersList = updatedUsersList[0]['channelMembers']
        else:
            return
        for i, channel in enumerate(channelList):
            if channel['channelId'] == channelId:
                del channelList[i]
                break
        for user in updatedUsersList:
            await self.active_connections[user].send_json({
                "deletedChannel":channelId,
                "loginType": 3
            })



manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    onlineUserList.append(client_id)
    await manager.user_status_boardcast(userId=client_id)
    try:
        while True:
            message = await websocket.receive_text()
            jsonString = json.loads(message)

            # messageType = 1: send text message
            if jsonString['messageType'] == 1:
                messagesHistory.append(jsonString)
                chatMode = jsonString['chatMode']
                match chatMode:
                    case 1:
                        await manager.send_personal_message(message, jsonString['receiverId'], jsonString['receiverName'],  jsonString['senderId'], jsonString['senderName'], websocket)
                    case 2:
                        await manager.send_channel_message(message)
                    # case 3:
                    #     await manager.send_edit_file(jsonString['content'], jsonString['channel'])
                    case _:
                        print("default")
            # messageType = 2: send file
            elif jsonString['messageType'] == 2:
                fileSent = await websocket.receive_bytes()
                chatMode = jsonString['chatMode']
                match chatMode:
                    case 1:
                        await manager.send_file_user(jsonString['file'], jsonString['channel'])
                    case 2:
                        await manager.send_file_channel(fileSent, jsonString['channel'])
                    case _:
                        print("default")
            # messageType = 4: create new channel
            elif jsonString['messageType'] == 3:
                await manager.send_edit_file(jsonString['senderId'], jsonString['fileId'], jsonString['content'])
            elif jsonString['messageType'] == 4:
                await manager.create_new_channel(jsonObject=jsonString)
            elif jsonString['messageType'] == 5:
                await manager.delete_channel(jsonString,channelId=jsonString['deleteChannel']['channelId'], websocket=websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
        onlineUserList.remove(client_id)
        await manager.user_status_boardcast(userId=client_id)