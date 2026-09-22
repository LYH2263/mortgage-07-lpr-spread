import pytest
from fastapi import HTTPException
from app import db, seed
from app.engines.amortization import equal_payment_schedule
from app.engines.lpr import compose_annual_rate
from app.schemas.rate_baseline import BaselineCreate, BaselineUpdate
from app.services.mortgage_service import MortgageService

@pytest.fixture()
def svc(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.db")
    seed.init_db()
    s = MortgageService()
    yield s
    s.close()

def test_compose_annual_rate():
    assert compose_annual_rate(3.6, 55) == 4.15
    assert compose_annual_rate(3.45, -50) == 2.95
    with pytest.raises(ValueError):
        compose_annual_rate(3.0, -400)

def test_negative_compose_rejected_on_create(svc):
    with pytest.raises(HTTPException) as ei:
        svc.create_baseline(BaselineCreate(name="bad", lpr=3.0, spread_bps=-400))
    assert ei.value.status_code == 422

def test_schedule_with_baseline(svc):
    b = svc.create_baseline(BaselineCreate(name="5Y", lpr=3.6, spread_bps=55))
    out = svc.schedule(1_000_000, 0, 360, None, False, baseline_id=b["id"])
    assert out["annual_rate"] == 4.15
    assert out["baseline_id"] == b["id"]
    direct = equal_payment_schedule(1_000_000, 4.15, 360)
    assert out["monthly_payment"] == direct["monthly_payment"]
    assert out["total_interest"] == direct["total_interest"]

def test_schedule_without_baseline_uses_body_rate(svc):
    out = svc.schedule(800_000, 4.2, 240, None, False)
    assert "baseline_id" not in out
    direct = equal_payment_schedule(800_000, 4.2, 240)
    assert out["monthly_payment"] == direct["monthly_payment"]
    assert out["annual_rate"] == 4.2

def test_persist_false_writes_nothing(svc):
    before = len(svc.history(100))
    b = svc.create_baseline(BaselineCreate(lpr=3.6, spread_bps=0))
    svc.schedule(500_000, 0, 120, None, False, baseline_id=b["id"])
    assert len(svc.history(100)) == before

def test_disabled_baseline_rejected(svc):
    b = svc.create_baseline(BaselineCreate(lpr=3.6, spread_bps=0))
    svc.update_baseline(b["id"], BaselineUpdate(enabled=False))
    with pytest.raises(HTTPException) as ei:
        svc.schedule(100_000, 0, 120, None, False, baseline_id=b["id"])
    assert ei.value.status_code == 422

def test_history_pinned_after_lpr_hike(svc):
    b = svc.create_baseline(BaselineCreate(name="5Y", lpr=3.6, spread_bps=55))
    out = svc.schedule(1_000_000, 0, 360, None, True, baseline_id=b["id"])
    svc.update_baseline(b["id"], BaselineUpdate(lpr=4.2))
    top = svc.history(10)[0]
    assert top["annual_rate"] == 4.15
    assert top["monthly_payment"] == out["monthly_payment"]
    assert top["total_interest"] == out["total_interest"]
    assert top["baseline_name"] == "5Y"
    # 基准本身已更新，仅历史条目不变
    assert svc.list_baselines()[0]["lpr"] == 4.2
