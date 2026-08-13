from typing import List
from pydantic import BaseModel, Field


class FactCheckItem(BaseModel):
    statement: str
    is_verified: bool
    source_url: str = ""
    notes: str = ""


class FactCheckReport(BaseModel):
    items: List[FactCheckItem] = Field(default_factory=list)
    overall_trust_score: float = Field(default=1.0, ge=0.0, le=1.0)
    hallucination_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    passed: bool = True
