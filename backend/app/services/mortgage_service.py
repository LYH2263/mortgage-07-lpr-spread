from fastapi import HTTPException
from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.engines.lpr import compose_annual_rate
from app.repositories import loans, runs, settings, rate_baselines

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50):
        items = runs.list_recent(self._c, limit)
        for it in items:
            it.update(runs.summarize(it))
        return items
    def list_baselines(self, enabled_only=False): return rate_baselines.list_all(self._c, enabled_only)
    def create_baseline(self, payload):
        try:
            compose_annual_rate(payload.lpr, payload.spread_bps)
        except ValueError:
            raise HTTPException(422, "合成年利率不得为负")
        return rate_baselines.insert(self._c, payload.name, payload.lpr, payload.spread_bps, payload.enabled)
    def update_baseline(self, bid, payload):
        row = rate_baselines.get(self._c, bid)
        if not row:
            raise HTTPException(404, "基准不存在")
        merged = {
            "name": row["name"] if payload.name is None else payload.name,
            "lpr": row["lpr"] if payload.lpr is None else payload.lpr,
            "spread_bps": row["spread_bps"] if payload.spread_bps is None else payload.spread_bps,
        }
        try:
            compose_annual_rate(merged["lpr"], merged["spread_bps"])
        except ValueError:
            raise HTTPException(422, "合成年利率不得为负")
        return rate_baselines.update(self._c, bid, payload.model_dump(exclude_none=True))
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12, baseline_id=None):
        baseline = None
        if baseline_id is not None:
            baseline = rate_baselines.get(self._c, baseline_id)
            if not baseline or not baseline["enabled"]:
                raise HTTPException(422, "基准不存在或已停用")
            annual_rate = compose_annual_rate(baseline["lpr"], baseline["spread_bps"])
        full = equal_payment_schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        # 钉选：历史只认落库时的合成年利率，之后调高 LPR 不影响旧条月供
        out["annual_rate"] = round(float(annual_rate), 6)
        if baseline:
            out["baseline_id"] = baseline["id"]
            out["baseline_name"] = baseline["name"]
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            payload = {"principal": principal, "annual_rate": annual_rate, "months": months}
            if baseline:
                payload["baseline_id"] = baseline["id"]
            rid = runs.insert(self._c, "schedule", payload, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
