from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ...core.database import get_db
from ...models.document import Conversation, Message
from ...services.rag import rag_service
from ...services.usage_service import usage_service

from ...core.auth import current_active_user
from ...models.user import User
from uuid import UUID
from ...core.rate_limiter import limiter

router = APIRouter()

# Keep paths relative to /api/v1 prefix
class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=5000)
    document_ids: Optional[List[str]] = None
    conversation_id: Optional[UUID] = None

@router.post("")
@router.post("/")
@limiter.limit("20/minute")
async def query_rag(
    request: Request,  # Required for rate limiter
    query_request: QueryRequest, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    # Check user quota before processing
    has_quota, error_msg, usage = await usage_service.check_and_update_quota(
        db, str(user.id), estimated_tokens=1000
    )
    if not has_quota:
        raise HTTPException(status_code=429, detail=error_msg)
    
    conversation_history = []
    
    # If conversation_id is provided, fetch history
    if query_request.conversation_id:
        # Check if conversation exists and belongs to user
        result = await db.execute(
            select(Conversation).filter(
                Conversation.id == query_request.conversation_id,
                Conversation.user_id == user.id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found or access denied")
            
        msg_result = await db.execute(
            select(Message).filter(Message.conversation_id == query_request.conversation_id).order_by(Message.timestamp)
        )
        messages = msg_result.scalars().all()
        conversation_history = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]
    
    # Perform RAG
    result = await rag_service.query(
        question=query_request.question,
        document_ids=query_request.document_ids,
        conversation_history=conversation_history,
        user_id=str(user.id)
    )
    
    # Track token usage (estimate from response length)
    # In production, you'd get actual token count from LLM API response
    estimated_tokens = len(result["answer"]) // 4  # Rough estimate: 1 token ≈ 4 chars
    await usage_service.add_tokens(db, str(user.id), estimated_tokens)

    # Save interactions if conversation_id exists
    if query_request.conversation_id:
        # User message
        user_msg = Message(
            conversation_id=query_request.conversation_id,
            role="user",
            content=query_request.question
        )
        db.add(user_msg)
        
        # Assistant message
        ai_msg = Message(
            conversation_id=query_request.conversation_id,
            role="assistant",
            content=result["answer"],
            sources=result["sources"]
        )
        db.add(ai_msg)
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        await db.commit()

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "conversation_id": query_request.conversation_id,
        "context": result.get("context_used", "")
    }

@router.post("/stream")
@limiter.limit("20/minute")
async def query_rag_stream(
    request: Request,  # Required for rate limiter
    query_request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    # Check user quota before processing
    has_quota, error_msg, usage = await usage_service.check_and_update_quota(
        db, str(user.id), estimated_tokens=1000
    )
    if not has_quota:
        raise HTTPException(status_code=429, detail=error_msg)
    
    conversation_history = []
    conversation = None
    
    if query_request.conversation_id:
        result = await db.execute(
            select(Conversation).filter(
                Conversation.id == query_request.conversation_id,
                Conversation.user_id == user.id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found or access denied")
            
        msg_result = await db.execute(
            select(Message).filter(Message.conversation_id == query_request.conversation_id).order_by(Message.timestamp)
        )
        msg_list = msg_result.scalars().all()
        conversation_history = [{"role": msg.role, "content": msg.content} for msg in msg_list]

    async def event_generator():
        full_response = ""
        async for chunk in rag_service.query_stream(
            question=query_request.question,
            document_ids=query_request.document_ids,
            conversation_history=conversation_history,
            user_id=str(user.id)
        ):
            full_response += chunk
            yield chunk

        # Track token usage after streaming completes
        estimated_tokens = len(full_response) // 4
        await usage_service.add_tokens(db, str(user.id), estimated_tokens)
        
        # After streaming is done, save to DB if conversation exists
        if query_request.conversation_id and conversation:
            # User message
            user_msg = Message(
                conversation_id=query_request.conversation_id,
                role="user",
                content=query_request.question
            )
            db.add(user_msg)
            
            # Assistant message
            ai_msg = Message(
                conversation_id=query_request.conversation_id,
                role="assistant",
                content=full_response,
                sources=[] # In streaming, we'll keep sources empty for now or handle separately
            )
            db.add(ai_msg)
            conversation.updated_at = datetime.utcnow()
            await db.commit()

    return StreamingResponse(event_generator(), media_type="text/plain")

# Removed redundant conversation routes (now in api/routes/conversations.py)
