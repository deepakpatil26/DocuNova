from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID

class MessageBase(BaseModel):
    role: str # 'user' or 'assistant'
    content: str
    sources: Optional[List[Any]] = None

class MessageCreate(MessageBase):
    conversation_id: UUID

class MessageResponse(MessageBase):
    id: UUID
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConversationDetail(ConversationResponse):
    messages: List[MessageResponse] = []
