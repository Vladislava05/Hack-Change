from fastapi import FastAPI

from src.routers import routers
from src.sockets import sockets_routers

app = FastAPI()

for router in routers:
    app.include_router(router)

for router in sockets_routers:
    app.include_router(router)
