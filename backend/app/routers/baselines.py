from fastapi import APIRouter, HTTPException
from app.schemas.rate_baseline import BaselineCreate, BaselineUpdate
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/baselines")
def list_baselines(enabled: bool = False):
    with MortgageService() as s:
        return {"items": s.list_baselines(enabled_only=enabled)}
@router.post("/baselines")
def create_baseline(body: BaselineCreate):
    with MortgageService() as s:
        return s.create_baseline(body)
@router.patch("/baselines/{baseline_id}")
def update_baseline(baseline_id: int, body: BaselineUpdate):
    with MortgageService() as s:
        return s.update_baseline(baseline_id, body)
@router.post("/baselines/{baseline_id}/disable")
def disable_baseline(baseline_id: int):
    with MortgageService() as s:
        if not s.update_baseline(baseline_id, BaselineUpdate(enabled=False)):
            raise HTTPException(404)
        return {"ok": True}
