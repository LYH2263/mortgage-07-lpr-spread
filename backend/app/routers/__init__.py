from fastapi import APIRouter
from app.routers import baselines, dashboard, history, loans, schedule, settings
api = APIRouter(prefix="/api")
for r in (dashboard, loans, schedule, history, settings, baselines): api.include_router(r.router)
