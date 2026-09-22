from fastapi import APIRouter
from app.routers import benchmarks, dashboard, history, loans, schedule, settings
api = APIRouter(prefix="/api")
for r in (dashboard, loans, schedule, history, settings, benchmarks): api.include_router(r.router)
