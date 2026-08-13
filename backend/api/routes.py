from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.flows.main_flow import MainContentFlow

router = APIRouter()


class GenerateContentRequest(BaseModel):
    topic: str


@router.post("/generate")
async def generate_content(request: GenerateContentRequest):
    if not request.topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    flow = MainContentFlow(topic=request.topic)
    result = await flow.execute()
    return result
