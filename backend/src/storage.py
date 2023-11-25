from src.utils.connection_manager import IConnectionManager, ConnectionManager

chat_managers: dict[int, IConnectionManager] = {}
audio_managers: dict[int, IConnectionManager] = {}


def create_manager_room(room_id):
    chat_managers[room_id] = ConnectionManager()
    audio_managers[room_id] = ConnectionManager()


def delete_manager_room(room_id):
    chat_managers[room_id] = ConnectionManager()
    audio_managers[room_id] = ConnectionManager()
