from pydantic import BaseModel


class DraftContent(BaseModel):
    title: str
    body: str
    target_audience: str = "General"
    word_count: int = 0
