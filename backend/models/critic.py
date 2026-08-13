from typing import List
from pydantic import BaseModel, Field


class CritiqueFeedback(BaseModel):
    clarity_score: float = Field(ge=0.0, le=10.0)
    engagement_score: float = Field(ge=0.0, le=10.0)
    suggestions: List[str] = Field(default_factory=list)
    approved: bool = False
