from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UsageStats(BaseModel):
    """Response model for user token usage statistics"""
    daily_remaining: int
    daily_limit: int
    daily_used: int
    daily_percentage: float
    monthly_remaining: int
    monthly_limit: int
    monthly_used: int
    monthly_percentage: float
    total_used: int
    total_requests: int
    resets_in: str

    class Config:
        from_attributes = True
