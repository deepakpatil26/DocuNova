from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth import current_active_user
from ...core.database import get_db
from ...models.document import Conversation, Document, Message
from ...models.user import User
from ...services.usage_service import usage_service
from ...schemas.usage import UsageStats

router = APIRouter()


@router.get("")
@router.get("/")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    docs_query = await db.execute(
        select(func.count(Document.id)).filter(Document.user_id == user.id)
    )
    conversations_query = await db.execute(
        select(func.count(Conversation.id)).filter(Conversation.user_id == user.id)
    )
    messages_query = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .filter(Conversation.user_id == user.id)
    )

    return {
        "documents": docs_query.scalar_one(),
        "conversations": conversations_query.scalar_one(),
        "messages": messages_query.scalar_one(),
    }


@router.get("/usage", response_model=UsageStats)
async def get_usage_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """
    Get current user's token usage statistics
    Shows daily/monthly limits, used tokens, and remaining quota
    """
    stats = await usage_service.get_usage_stats(db, str(user.id))
    return stats

