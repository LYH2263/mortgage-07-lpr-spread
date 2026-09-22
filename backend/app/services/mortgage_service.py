from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.modules.rate_float import synthesized_annual_rate
from app.repositories import benchmarks, loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def list_benchmarks(self): return benchmarks.list_all(self._c)
    def benchmark(self, bid): return benchmarks.get(self._c, bid)
    def create_benchmark(self, name, lpr, spread_bp):
        synthesized_annual_rate(lpr, spread_bp)
        return benchmarks.get(self._c, benchmarks.insert(self._c, name, lpr, spread_bp))
    def update_benchmark(self, bid, name, lpr, spread_bp):
        synthesized_annual_rate(lpr, spread_bp)
        if not benchmarks.update(self._c, bid, name, lpr, spread_bp):
            raise LookupError("benchmark")
        return benchmarks.get(self._c, bid)
    def set_benchmark_enabled(self, bid, enabled):
        if not benchmarks.set_enabled(self._c, bid, enabled):
            raise LookupError("benchmark")
        return benchmarks.get(self._c, bid)
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12, benchmark_id=None):
        bench = None
        if benchmark_id is not None:
            bench = benchmarks.get(self._c, benchmark_id)
            if not bench:
                raise LookupError("benchmark")
            if not bench["enabled"]:
                raise ValueError("benchmark disabled")
            annual_rate = synthesized_annual_rate(bench["lpr"], bench["spread_bp"])
        full = equal_payment_schedule(principal, annual_rate, months)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["annual_rate"] = annual_rate
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        if bench:
            out["benchmark"] = {"id": bench["id"], "name": bench["name"], "lpr": bench["lpr"], "spread_bp": bench["spread_bp"]}
        rid = None
        if persist:
            payload = {"principal": principal, "annual_rate": annual_rate, "months": months}
            if bench:
                payload["benchmark_id"] = bench["id"]
            rid = runs.insert(self._c, "schedule", payload, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
