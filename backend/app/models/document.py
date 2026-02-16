from sqlalchemy import Column, String, Integer, DateTime, Text, Float, JSON, ForeignKey, UUID
from datetime import datetime
import uuid
from ..core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)

    # Processing metadata
    total_pages = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed

    # Qdrant reference
    qdrant_collection_id = Column(String(255), nullable=True)

    # Metadata
    metadata_ = Column("metadata", JSON, nullable=True) 

    def __repr__(self):
        return f"<Document {self.filename}>"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Conversation {self.id}>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Store source citations
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.role}: {self.content[:50]}>"
