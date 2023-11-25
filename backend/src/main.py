from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers import routers
from src.sockets import sockets_routers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in routers:
    app.include_router(router)

for router in sockets_routers:
    app.include_router(router)


