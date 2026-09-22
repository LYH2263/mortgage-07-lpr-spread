from fastapi import APIRouter, HTTPException
from app.schemas.benchmark import BenchmarkIn
from app.services.mortgage_service import MortgageService

router = APIRouter()

@router.get("/benchmarks")
def list_benchmarks():
    with MortgageService() as s:
        return {"items": s.list_benchmarks()}

@router.post("/benchmarks", status_code=201)
def create_benchmark(body: BenchmarkIn):
    with MortgageService() as s:
        return s.create_benchmark(body.name, body.lpr, body.spread_bp)

@router.put("/benchmarks/{bid}")
def update_benchmark(bid: int, body: BenchmarkIn):
    with MortgageService() as s:
        try:
            return s.update_benchmark(bid, body.name, body.lpr, body.spread_bp)
        except LookupError:
            raise HTTPException(404)

@router.post("/benchmarks/{bid}/disable")
def disable_benchmark(bid: int):
    with MortgageService() as s:
        try:
            return s.set_benchmark_enabled(bid, False)
        except LookupError:
            raise HTTPException(404)

@router.post("/benchmarks/{bid}/enable")
def enable_benchmark(bid: int):
    with MortgageService() as s:
        try:
            return s.set_benchmark_enabled(bid, True)
        except LookupError:
            raise HTTPException(404)
