from pydantic import BaseModel, Field, model_validator
from app.modules.rate_float import synthesized_annual_rate

class BenchmarkIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    lpr: float = Field(ge=0, le=100)
    spread_bp: float = 0

    @model_validator(mode="after")
    def _rate_not_negative(self):
        synthesized_annual_rate(self.lpr, self.spread_bp)
        return self
