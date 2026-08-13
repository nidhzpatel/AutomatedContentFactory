from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.models.research import ResearchOutput
from backend.models.draft import DraftContent
from backend.models.critic import CritiqueFeedback
from backend.models.edited import EditedContent
from backend.models.fact_check import FactCheckReport
from backend.models.social import SocialMediaCampaign


class FlowState(BaseModel):
    topic: str
    research: Optional[ResearchOutput] = None
    draft: Optional[DraftContent] = None
    critique: Optional[CritiqueFeedback] = None
    edited: Optional[EditedContent] = None
    fact_check: Optional[FactCheckReport] = None
    social: Optional[SocialMediaCampaign] = None
    
    # Execution Metrics & State Control
    revision_count: int = 0
    max_revisions: int = 3
    latency_ms: float = 0.0
    fact_check_score: float = 1.0
    hallucination_rate: float = 0.0
    status: str = "initialized"
    error_message: Optional[str] = None
