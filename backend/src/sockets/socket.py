from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.database.database import get_db
from src.security import get_current_user
from src.storage import audio_managers
from src.utils.dependencies import UOWDep

router = APIRouter(prefix="/ws", tags=["WebSockets"], responses={404: {"description": "Not found"}})


@router.websocket("/{room_id}")
async def audio_websocket_endpoint(
    uow: UOWDep, websocket: WebSocket, room_id: int, token: str, db: AsyncSession = Depends(get_db)
):
    user = await get_current_user(token, db)
    manager = audio_managers[room_id]
    await manager.connect(websocket, user)
    if room_id not in audio_managers:
        await manager.send_message("Комнаты с таким id не существует")
        manager.disconnect(websocket, user)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user)
        async with uow:
            user_in_room = await uow.users_rooms.find_one(user_id=user.id)
            await uow.users_rooms.delete_one(user_id=user.id)

            if user_in_room.is_leader:
                if manager.active_connections:
                    await uow.users_rooms.edit_one(user_id=manager.active_connections[0].user, data={"is_leader": True})
                else:
                    await uow.rooms.delete_one(id=room_id)
