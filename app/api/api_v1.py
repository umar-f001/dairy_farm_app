from fastapi import APIRouter

from app.api.endpoints import animals
from app.api.endpoints import milk_tracking
from app.api.endpoints import feed
from app.api.endpoints import agent
from app.api.endpoints import dummy

api_router = APIRouter()

api_router.include_router(animals.router)
api_router.include_router(milk_tracking.router)
api_router.include_router(feed.router)
api_router.include_router(agent.router)
api_router.include_router(dummy.router)
