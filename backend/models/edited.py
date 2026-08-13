from typing import List
from pydantic import BaseModel, Field


class EditedContent(BaseModel):
    title: str
    body: str
    changes_made: List[str] = Field(default_factory=list)
    word_count: int = 0
