import json
import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="mortgage-test-")

import pytest

from app import seed
from app.modules.rate_float import synthesized_annual_rate
from app.services.mortgage_service import MortgageService

seed.init_db()


def test_synth_rate_adds_bp():
    assert synthesized_annual_rate(3.6, 50) == 4.1

def test_synth_rate_negative_bp():
    assert synthesized_annual_rate(3.85, -20) == 3.65

def test_synth_rate_must_not_be_negative():
    with pytest.raises(ValueError):
        synthesized_annual_rate(0.1, -20)

def test_benchmark_crud_and_disable():
    with MortgageService() as s:
        b = s.create_benchmark("首套", 3.6, -20)
        assert b["enabled"] is True
        assert b["id"] in [x["id"] for x in s.list_benchmarks()]
        b = s.update_benchmark(b["id"], "首套改", 3.7, 10)
        assert (b["name"], b["lpr"], b["spread_bp"]) == ("首套改", 3.7, 10)
        b = s.set_benchmark_enabled(b["id"], False)
        assert b["enabled"] is False
        b = s.set_benchmark_enabled(b["id"], True)
        assert b["enabled"] is True

def test_update_missing_benchmark_raises():
    with MortgageService() as s:
        with pytest.raises(LookupError):
            s.update_benchmark(999999, "无", 3.6, 0)

def test_negative_synth_rate_rejected_on_write():
    with MortgageService() as s:
        with pytest.raises(ValueError):
            s.create_benchmark("负利率", 0.1, -20)

def test_schedule_with_benchmark_returns_synth_rate():
    with MortgageService() as s:
        b = s.create_benchmark("基准A", 3.6, 50)
        out = s.schedule(1_000_000, 9.9, 360, None, False, 12, b["id"])
        assert out["annual_rate"] == 4.1
        assert out["benchmark"]["id"] == b["id"]
        assert out["monthly_payment"] > 0
        assert out["total_interest"] > 0
        assert out["run_id"] is None

def test_schedule_without_benchmark_uses_body_rate():
    with MortgageService() as s:
        out = s.schedule(1_000_000, 3.5, 360, None, False)
        assert out["annual_rate"] == 3.5
        assert out["monthly_payment"] == 4490.45
        assert "benchmark" not in out

def test_persist_false_writes_nothing():
    with MortgageService() as s:
        before = len(s.history(10000))
        b = s.create_benchmark("基准B", 3.6, 0)
        s.schedule(100_000, 3.0, 12, None, False, 12, b["id"])
        s.schedule(100_000, 3.0, 12, None, False)
        assert len(s.history(10000)) == before

def test_disabled_benchmark_rejected():
    with MortgageService() as s:
        b = s.create_benchmark("停用基准", 3.6, 0)
        s.set_benchmark_enabled(b["id"], False)
        with pytest.raises(ValueError):
            s.schedule(100_000, 3.0, 12, None, False, 12, b["id"])

def test_missing_benchmark_raises():
    with MortgageService() as s:
        with pytest.raises(LookupError):
            s.schedule(100_000, 3.0, 12, None, False, 12, 999999)

def test_history_pins_synth_rate_after_lpr_hike():
    with MortgageService() as s:
        b = s.create_benchmark("钉选", 3.0, 0)
        r1 = s.schedule(1_000_000, 9.9, 360, None, True, 12, b["id"])
        assert r1["annual_rate"] == 3.0
        s.update_benchmark(b["id"], "钉选", 4.5, 0)
        rec = {h["id"]: h for h in s.history(10000)}[r1["run_id"]]
        pinned_in = json.loads(rec["input_json"])
        pinned_out = json.loads(rec["result_json"])
        assert pinned_in["annual_rate"] == 3.0
        assert pinned_in["benchmark_id"] == b["id"]
        assert pinned_out["annual_rate"] == 3.0
        assert pinned_out["monthly_payment"] == r1["monthly_payment"]
        r2 = s.schedule(1_000_000, 9.9, 360, None, False, 12, b["id"])
        assert r2["annual_rate"] == 4.5
        assert r2["monthly_payment"] != r1["monthly_payment"]
