from pydantic import BaseModel, Field

class BaselineCreate(BaseModel):
    name: str = ""
    lpr: float = Field(ge=0)
    spread_bps: float = 0
    enabled: bool = True

class BaselineUpdate(BaseModel):
    name: str | None = None
    lpr: float | None = Field(default=None, ge=0)
    spread_bps: float | None = None
    enabled: bool | None = None
