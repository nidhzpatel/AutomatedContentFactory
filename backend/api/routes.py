from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.api.dependencies import get_settings
from backend.flows.main_flow import MainContentFlow

router = APIRouter()


class GenerateContentRequest(BaseModel):
    topic: str


@router.post("/generate")
async def generate_content(request: GenerateContentRequest, app_settings=Depends(get_settings)):
    if not request.topic or not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")

    flow = MainContentFlow(topic=request.topic)
    result = await flow.execute()
    result["meta"] = {
        "project": app_settings.PROJECT_NAME,
        "environment": app_settings.ENVIRONMENT,
    }
    return result
