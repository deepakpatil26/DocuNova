from sqlalchemy import Column, String, Integer, DateTime, BigInteger, ForeignKey
from datetime import datetime, timedelta
import uuid
from ..core.database import Base

class UserUsage(Base):
    """
    Track token usage per user for quota management
    """
    __tablename__ = "user_usage"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False, index=True)
    
    # Token tracking
    tokens_used_today = Column(BigInteger, default=0)
    tokens_used_this_month = Column(BigInteger, default=0)
    total_tokens_used = Column(BigInteger, default=0)
    
    # Quotas (can be customized per user)
    daily_token_limit = Column(BigInteger, default=300000)  # 300K tokens/day (like bolt.new)
    monthly_token_limit = Column(BigInteger, default=5000000)  # 5M tokens/month
    
    # Request tracking
    requests_today = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    
    # Timestamps for reset logic
    last_daily_reset = Column(DateTime, default=datetime.utcnow)
    last_monthly_reset = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserUsage user_id={self.user_id} tokens_today={self.tokens_used_today}>"
    
    def reset_daily_if_needed(self):
        """Reset daily counters if 24 hours have passed"""
        now = datetime.utcnow()
        if now - self.last_daily_reset >= timedelta(days=1):
            self.tokens_used_today = 0
            self.requests_today = 0
            self.last_daily_reset = now
            return True
        return False
    
    def reset_monthly_if_needed(self):
        """Reset monthly counters if 30 days have passed"""
        now = datetime.utcnow()
        if now - self.last_monthly_reset >= timedelta(days=30):
            self.tokens_used_this_month = 0
            self.last_monthly_reset = now
            return True
        return False
    
    def has_quota_remaining(self) -> tuple[bool, str]:
        """
        Check if user has quota remaining
        Returns: (has_quota, error_message)
        """
        self.reset_daily_if_needed()
        self.reset_monthly_if_needed()
        
        if self.tokens_used_today >= self.daily_token_limit:
            return False, f"Daily token limit reached ({self.daily_token_limit:,} tokens). Resets in {self._time_until_daily_reset()}."
        
        if self.tokens_used_this_month >= self.monthly_token_limit:
            return False, f"Monthly token limit reached ({self.monthly_token_limit:,} tokens). Resets in {self._time_until_monthly_reset()}."
        
        return True, ""
    
    def _time_until_daily_reset(self) -> str:
        """Calculate time remaining until daily reset"""
        reset_time = self.last_daily_reset + timedelta(days=1)
        remaining = reset_time - datetime.utcnow()
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def _time_until_monthly_reset(self) -> str:
        """Calculate time remaining until monthly reset"""
        reset_time = self.last_monthly_reset + timedelta(days=30)
        remaining = reset_time - datetime.utcnow()
        days = remaining.days
        return f"{days} days"
    
    def add_tokens(self, token_count: int):
        """Add tokens to usage counters"""
        self.tokens_used_today += token_count
        self.tokens_used_this_month += token_count
        self.total_tokens_used += token_count
        self.requests_today += 1
        self.total_requests += 1
    
    def get_remaining_tokens(self) -> dict:
        """Get remaining token counts"""
        self.reset_daily_if_needed()
        self.reset_monthly_if_needed()
        
        return {
            "daily_remaining": max(0, self.daily_token_limit - self.tokens_used_today),
            "daily_limit": self.daily_token_limit,
            "daily_used": self.tokens_used_today,
            "daily_percentage": round((self.tokens_used_today / self.daily_token_limit) * 100, 1),
            "monthly_remaining": max(0, self.monthly_token_limit - self.tokens_used_this_month),
            "monthly_limit": self.monthly_token_limit,
            "monthly_used": self.tokens_used_this_month,
            "monthly_percentage": round((self.tokens_used_this_month / self.monthly_token_limit) * 100, 1),
            "total_used": self.total_tokens_used,
            "total_requests": self.total_requests,
            "resets_in": self._time_until_daily_reset()
        }
