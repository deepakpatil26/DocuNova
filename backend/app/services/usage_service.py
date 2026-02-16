from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.usage import UserUsage
from ..models.user import User
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class UsageService:
    """Service for tracking and managing user token usage"""
    
    @staticmethod
    async def get_or_create_usage(db: AsyncSession, user_id: str) -> UserUsage:
        """Get existing usage record or create new one for user"""
        result = await db.execute(
            select(UserUsage).filter(UserUsage.user_id == user_id)
        )
        usage = result.scalar_one_or_none()
        
        if not usage:
            usage = UserUsage(user_id=user_id)
            db.add(usage)
            await db.commit()
            await db.refresh(usage)
            logger.info(f"Created new usage record for user {user_id}")
        
        return usage
    
    @staticmethod
    async def check_and_update_quota(
        db: AsyncSession, 
        user_id: str, 
        estimated_tokens: int = 0
    ) -> tuple[bool, str, Optional[UserUsage]]:
        """
        Check if user has quota and update counters
        Returns: (has_quota, error_message, usage_record)
        """
        usage = await UsageService.get_or_create_usage(db, user_id)
        
        # Check quota
        has_quota, error_msg = usage.has_quota_remaining()
        
        if not has_quota:
            logger.warning(f"User {user_id} exceeded quota: {error_msg}")
            return False, error_msg, usage
        
        # If estimated tokens provided, check if it would exceed quota
        if estimated_tokens > 0:
            if usage.tokens_used_today + estimated_tokens > usage.daily_token_limit:
                return False, f"Request would exceed daily token limit", usage
        
        return True, "", usage
    
    @staticmethod
    async def add_tokens(
        db: AsyncSession, 
        user_id: str, 
        token_count: int
    ) -> UserUsage:
        """Add tokens to user's usage counters"""
        usage = await UsageService.get_or_create_usage(db, user_id)
        usage.add_tokens(token_count)
        await db.commit()
        await db.refresh(usage)
        
        logger.info(f"Added {token_count} tokens for user {user_id}. Daily total: {usage.tokens_used_today}")
        return usage
    
    @staticmethod
    async def get_usage_stats(db: AsyncSession, user_id: str) -> dict:
        """Get usage statistics for a user"""
        usage = await UsageService.get_or_create_usage(db, user_id)
        return usage.get_remaining_tokens()
    
    @staticmethod
    async def reset_user_quota(db: AsyncSession, user_id: str, reset_type: str = "daily"):
        """Admin function to manually reset user quota"""
        usage = await UsageService.get_or_create_usage(db, user_id)
        
        if reset_type == "daily":
            usage.tokens_used_today = 0
            usage.requests_today = 0
        elif reset_type == "monthly":
            usage.tokens_used_this_month = 0
        elif reset_type == "all":
            usage.tokens_used_today = 0
            usage.tokens_used_this_month = 0
            usage.requests_today = 0
        
        await db.commit()
        logger.info(f"Reset {reset_type} quota for user {user_id}")
        return usage

# Singleton instance
usage_service = UsageService()
