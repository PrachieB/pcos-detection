from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class PredictRequest(BaseModel):
    tier: Literal[1, 2] = 1
    age: int = Field(ge=12, le=60)
    bmi: float = Field(ge=12, le=55)
    cycle_irregular: Literal[0, 1]
    weight_gain: Literal[0, 1]
    hair_growth: Literal[0, 1]
    skin_darkening: Literal[0, 1]
    hair_loss: Literal[0, 1]
    pimples: Literal[0, 1]
    fast_food: Literal[0, 1]
    regular_exercise: Literal[0, 1]
    # Tier 2 only
    follicle_l: Optional[int] = Field(default=None, ge=0, le=40)
    follicle_r: Optional[int] = Field(default=None, ge=0, le=40)
    amh: Optional[float] = Field(default=None, ge=0, le=30)
    fsh_lh: Optional[float] = Field(default=None, ge=0, le=20)

    @model_validator(mode="after")
    def tier2_needs_labs(self):
        if self.tier == 2:
            missing = [k for k in ("follicle_l", "follicle_r", "amh", "fsh_lh")
                       if getattr(self, k) is None]
            if missing:
                raise ValueError(f"Tier 2 needs: {', '.join(missing)}")
        return self


class Factor(BaseModel):
    feature: str
    label: str
    value: float
    contribution: float
    direction: Literal["raises", "lowers"]


class PredictResponse(BaseModel):
    tier: int
    risk: float
    risk_percent: float
    band: Literal["low", "moderate", "high"]
    headline: str
    advice: list[str]
    factors: list[Factor]
    demo_model: bool
    disclaimer: str
