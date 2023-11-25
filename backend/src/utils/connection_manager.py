from abc import ABC, abstractmethod
from dataclasses import dataclass

from fastapi import WebSocket

from src.models.users import Users


@dataclass
class Connection:
    websocket: WebSocket
    user: Users


class IConnectionManager(ABC):
    active_connections: list[Connection]

    @abstractmethod
    async def connect(self, websocket: WebSocket, user: Users):
        raise NotImplementedError

    @abstractmethod
    async def send_message(self, message: str):
        raise NotImplementedError

    @abstractmethod
    def disconnect(self, websocket: WebSocket, user: Users):
        raise NotImplementedError


class ConnectionManager(IConnectionManager):
    def __init__(self):
        self.active_connections: list[Connection] = []

    async def connect(self, websocket: WebSocket, user: Users):
        await websocket.accept()
        self.active_connections.append(Connection(websocket, user))

    async def send_message(self, message: str):
        for con in self.active_connections:
            await con.websocket.send_text(message)

    def disconnect(self, websocket: WebSocket, user: Users):
        self.active_connections.remove(Connection(websocket, user))
