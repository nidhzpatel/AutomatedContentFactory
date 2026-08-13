from typing import List
from pydantic import BaseModel, Field


class ResearchSource(BaseModel):
    title: str
    url: str
    snippet: str


class ResearchOutput(BaseModel):
    topic: str
    key_findings: List[str] = Field(default_factory=list)
    sources: List[ResearchSource] = Field(default_factory=list)
    summary: str
