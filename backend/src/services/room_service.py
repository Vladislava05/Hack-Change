from fastapi import HTTPException, status

from src.models.users import Users
from src.schemas.room import UsersRoomsAdd, UsersIdScheme
from src.storage import create_manager_room, delete_manager_room
from src.utils.dependencies import UOWDep


async def check_user_in_room(uow: UOWDep, user_id: int):
    user_in_room = await uow.users_rooms.find_one(user_id=user_id, no_error=True)
    if user_in_room:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Вы уже состоите в какой-то комнате. Проверте сессии"
        )
    return user_in_room


async def is_leader(uow, id):
    user_in_room = await uow.users_rooms.find_one(user_id=id)
    if not user_in_room.is_leader:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы не лидер комнаты.")


async def get_room(
    room_id: int,
    uow: UOWDep,
):
    async with uow:
        users = await uow.rooms.find_one(id=room_id)
        return users


async def add_room(uow: UOWDep, user: Users):
    async with uow:
        await check_user_in_room(uow, user.id)
        room = await uow.rooms.add_one({})
        await uow.users_rooms.add_one({"room_id": room.id, "user_id": user.id, "is_leader": True})
        create_manager_room(room.id)
        return room.to_read_model()


async def delete_room(uow: UOWDep, room_id: int, user: Users):
    async with uow:
        await is_leader(uow, user.id)
        await uow.rooms.delete_one(id=room_id)
        delete_manager_room(room_id)


async def add_user_room(uow: UOWDep, data: UsersRoomsAdd, user: Users):
    async with uow:
        await check_user_in_room(uow, user.id)
        await uow.users_rooms.add_one({"room_id": data.room_id, "user_id": user.id})


async def remove_users_room(uow: UOWDep, user_id: int, user: Users):
    async with uow:
        await is_leader(uow, user.id)
        user_in_room = await uow.users_rooms.find_one(user_id=user_id, no_error=True)
        if not user_in_room:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Пользователь не состоите в комнате."
            )
        await uow.users_rooms.delete_one(user_id=user_id)


async def get_users_room(uow: UOWDep, room_id: int):
    async with uow:
        users = await uow.users_rooms.find_users_room(room_id=room_id)
        return users


async def set_leaders(uow: UOWDep, data: UsersIdScheme, user: Users):
    async with uow:
        await is_leader(uow, user.id)
        await uow.users_rooms.edit_one(user.id, {"is_leader": False})
        await uow.users_rooms.edit_one(data.user_id, {"is_leader": True})
