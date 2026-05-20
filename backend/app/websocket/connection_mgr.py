import uuid
from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket]={}

    def generate_session_id(self) -> str:
        return str(uuid.uuid4())[:8]
    
    async def connect(self, websocket: WebSocket) -> str:
        await websocket.accept()
        session_id=self.generate_session_id()
        self.active_connections[session_id]=websocket
        print(f"client connected: {session_id}")
        print(f"active connections: {len(self.active_connections)}")
        return session_id
    
    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)
        print(f"client disconnected: {session_id}")
        print(f"active connections: {len(self.active_connections)}")

    async def send_message(self, session_id: str, message: str):
        websocket=self.active_connections.get(session_id)
        if websocket:
            await websocket.send_text(message)

    @property
    def connection_count(self)->int:
        return len(self.active_connections)
    
connection_mgr=ConnectionManager()