from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from base64 import urlsafe_b64encode, urlsafe_b64decode
import hashlib
import hmac

from ...core.database import get_db
from ...models.document import Conversation, Message
from ...schemas.conversation import ConversationCreate, ConversationResponse, MessageResponse, ConversationDetail
from ...core.auth import current_active_user
from ...models.user import User
from ...services.rag import rag_service
from ...core.config import settings

router = APIRouter()


class ConversationMessageRequest(BaseModel):
    question: str = Field(min_length=2, max_length=5000)
    document_ids: List[str] | None = None


def _build_share_token(conversation_id: UUID, owner_id: UUID) -> str:
    payload = f"{conversation_id}:{owner_id}".encode("utf-8")
    sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    raw = f"{conversation_id}:{owner_id}:{sig}".encode("utf-8")
    return urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _parse_share_token(token: str) -> tuple[UUID, UUID]:
    padded = token + "=" * ((4 - len(token) % 4) % 4)
    decoded = urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
    conversation_id_s, owner_id_s, sig = decoded.split(":")
    payload = f"{conversation_id_s}:{owner_id_s}".encode("utf-8")
    expected = hmac.new(settings.SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise HTTPException(status_code=400, detail="Invalid share token")
    return UUID(conversation_id_s), UUID(owner_id_s)

@router.post("", response_model=ConversationResponse)
@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conv_in: ConversationCreate, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """Create a new conversation session"""
    db_conv = Conversation(title=conv_in.title, user_id=user.id)
    db.add(db_conv)
    await db.commit()
    await db.refresh(db_conv)
    return db_conv

@router.get("", response_model=List[ConversationResponse])
@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """List all conversations"""
    query = select(Conversation).filter(Conversation.user_id == user.id)
    if q:
        query = query.filter(Conversation.title.ilike(f"%{q}%"))

    result = await db.execute(query.order_by(Conversation.updated_at.desc()))
    return result.scalars().all()

@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """Get conversation details with messages"""
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    db_conv = result.scalar_one_or_none()
    if not db_conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    msg_result = await db.execute(
        select(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc())
    )
    messages = msg_result.scalars().all()
    
    # Manually build the response for now until we have proper relationships
    return {
        "id": db_conv.id,
        "title": db_conv.title,
        "created_at": db_conv.created_at,
        "updated_at": db_conv.updated_at,
        "messages": messages
    }

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """Delete a conversation and its messages"""
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    db_conv = result.scalar_one_or_none()
    if not db_conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete messages first
    await db.execute(delete(Message).filter(Message.conversation_id == conversation_id))
    # Delete session
    await db.delete(db_conv)
    await db.commit()
    return None


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def list_conversation_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    db_conv = result.scalar_one_or_none()
    if not db_conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_result = await db.execute(
        select(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc())
    )
    return msg_result.scalars().all()


@router.post("/{conversation_id}/messages")
async def send_conversation_message(
    conversation_id: UUID,
    request: ConversationMessageRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_result = await db.execute(
        select(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc())
    )
    history_messages = msg_result.scalars().all()
    conversation_history = [{"role": msg.role, "content": msg.content} for msg in history_messages]

    rag_result = await rag_service.query(
        question=request.question,
        document_ids=request.document_ids,
        conversation_history=conversation_history,
        user_id=str(user.id)
    )

    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=request.question
    )
    assistant_msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=rag_result["answer"],
        sources=rag_result["sources"]
    )
    db.add(user_msg)
    db.add(assistant_msg)
    conversation.updated_at = datetime.utcnow()
    await db.commit()

    return {
        "answer": rag_result["answer"],
        "sources": rag_result["sources"],
        "conversation_id": str(conversation_id)
    }


@router.get("/{conversation_id}/export")
async def export_conversation(
    conversation_id: UUID,
    format: str = "md",
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg_result = await db.execute(
        select(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc())
    )
    messages = msg_result.scalars().all()

    lines: list[str] = []
    title = conversation.title or f"Conversation {conversation_id}"
    lines.append(f"# {title}")
    lines.append("")
    for msg in messages:
        role = "User" if msg.role == "user" else "Assistant"
        lines.append(f"## {role}")
        lines.append(msg.content)
        if msg.sources:
            lines.append("")
            lines.append("Sources:")
            for src in msg.sources:
                filename = src.get("filename", "Unknown")
                page = src.get("page")
                citation = f"- {filename}" + (f" (p. {page})" if page else "")
                lines.append(citation)
        lines.append("")

    content = "\n".join(lines).strip() + "\n"
    filename = f"conversation-{conversation_id}.{ 'txt' if format == 'txt' else 'md'}"

    if format == "txt":
        content = content.replace("# ", "").replace("## ", "")

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return PlainTextResponse(content=content, headers=headers)


@router.post("/{conversation_id}/share")
async def create_share_link(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    token = _build_share_token(conversation_id, user.id)
    return {"share_token": token, "share_path": f"/api/v1/conversations/shared/{token}"}


@router.get("/shared/{token}", response_model=ConversationDetail)
async def get_shared_conversation(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    conversation_id, owner_id = _parse_share_token(token)
    result = await db.execute(
        select(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == owner_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Shared conversation not found")

    msg_result = await db.execute(
        select(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc())
    )
    messages = msg_result.scalars().all()

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": messages,
    }
