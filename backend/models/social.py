from typing import List
from pydantic import BaseModel, Field


class SocialPost(BaseModel):
    platform: str
    content: str
    hashtags: List[str] = Field(default_factory=list)


class SocialMediaCampaign(BaseModel):
    posts: List[SocialPost] = Field(default_factory=list)
