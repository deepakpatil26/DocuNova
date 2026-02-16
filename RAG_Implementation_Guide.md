# RAG Project - Technical Implementation Guide

## 📁 Complete Project Structure

```text
docuchat/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # Settings & env vars
│   │   │   ├── database.py            # DB connection
│   │   │   └── security.py            # Auth utilities
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── document.py            # SQLAlchemy models
│   │   │   └── conversation.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── document.py            # Pydantic schemas
│   │   │   └── query.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py  # PDF parsing, chunking
│   │   │   ├── embeddings.py          # Embedding generation
│   │   │   ├── vector_store.py        # Qdrant operations
│   │   │   ├── llm.py                 # LLM integration
│   │   │   └── rag.py                 # RAG orchestration
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── documents.py       # Document endpoints
│   │   │       ├── query.py           # Query endpoints
│   │   │       └── health.py          # Health check
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py              # Logging setup
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_document_processor.py
│   │   ├── test_rag.py
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Navbar.tsx
│   │   │   │   └── Sidebar.tsx
│   │   │   ├── Upload/
│   │   │   │   ├── FileUploader.tsx
│   │   │   │   └── UploadProgress.tsx
│   │   │   ├── Chat/
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── InputBox.tsx
│   │   │   │   └── SourceCard.tsx
│   │   │   └── Documents/
│   │   │       ├── DocumentList.tsx
│   │   │       └── DocumentCard.tsx
│   │   ├── hooks/
│   │   │   ├── useDocuments.ts
│   │   │   ├── useChat.ts
│   │   │   └── useUpload.ts
│   │   ├── services/
│   │   │   └── api.ts                 # Axios instance
│   │   ├── types/
│   │   │   └── index.ts               # TypeScript types
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Chat.tsx
│   │   │   └── Documents.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── .env.example
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml                     # CI/CD pipeline
└── README.md
```

---

## 🔧 Step 1: Backend Setup

### **1.1 Create `requirements.txt`**

```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Vector Database
qdrant-client==1.7.3

# Document Processing
PyPDF2==3.0.1
pdfplumber==0.10.3
python-multipart==0.0.6
chardet==5.2.0

# Embeddings & LLM
sentence-transformers==2.3.1
groq==0.4.1
openai==1.10.0
langchain==0.1.6
langchain-community==0.0.17

# Utilities
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0
aiofiles==23.2.1

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0

# Monitoring
sentry-sdk[fastapi]==1.40.0
```

### **1.2 Create `backend/app/core/config.py`**

```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "DocuChat"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Qdrant Vector Database
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "documents"

    # LLM Configuration
    GROQ_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "llama-3.1-70b-versatile"  # Groq model

    # Embedding Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Document Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt", ".md"}
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # RAG Configuration
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # Sentry (optional)
    SENTRY_DSN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### **1.3 Create `backend/app/core/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **1.4 Create `backend/app/models/document.py`**

```python
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from ..core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<Document {self.filename}>"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Conversation {self.id}>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Store source citations
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.role}: {self.content[:50]}>"
```

### **1.5 Create `backend/app/services/embeddings.py`**

```python
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from ..core.config import settings

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()

# Singleton instance
embedding_service = EmbeddingService()
```

### **1.6 Create `backend/app/services/document_processor.py`**

```python
import PyPDF2
import pdfplumber
from typing import List, Dict, Any
from pathlib import Path
import re
from ..core.config import settings

class Chunk:
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata

class DocumentProcessor:

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text and metadata from PDF"""
        text = ""
        metadata = {
            "total_pages": 0,
            "page_texts": {}
        }

        try:
            # Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(file_path) as pdf:
                metadata["total_pages"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                    metadata["page_texts"][page_num] = page_text

        except Exception as e:
            # Fallback to PyPDF2
            print(f"pdfplumber failed, using PyPDF2: {e}")
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata["total_pages"] = len(pdf_reader.pages)

                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    page_text = page.extract_text() or ""
                    text += f"\n\n--- Page {page_num} ---\n\n{page_text}"
                    metadata["page_texts"][page_num] = page_text

        return text.strip(), metadata

    @staticmethod
    def extract_text_from_txt(file_path: str) -> tuple[str, Dict[str, Any]]:
        """Extract text from plain text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        metadata = {
            "total_pages": 1,
            "line_count": len(text.split('\n'))
        }

        return text, metadata

    @staticmethod
    def smart_chunk(text: str, document_id: str, filename: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Intelligent chunking that preserves context
        """
        chunks = []

        # Clean text
        text = re.sub(r'\n{3,}', '\n\n', text)  # Remove excessive newlines

        # Split by pages if available
        if "page_texts" in metadata:
            for page_num, page_text in metadata["page_texts"].items():
                page_chunks = DocumentProcessor._chunk_text(
                    page_text,
                    {
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_num,
                        "total_pages": metadata.get("total_pages", 1)
                    }
                )
                chunks.extend(page_chunks)
        else:
            # No page info, chunk the whole text
            chunks = DocumentProcessor._chunk_text(
                text,
                {
                    "document_id": document_id,
                    "filename": filename,
                    "page": 1
                }
            )

        return chunks

    @staticmethod
    def _chunk_text(text: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
        """Helper function to chunk text with overlap"""
        chunks = []

        # Split by sentences (rough)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current_chunk = ""
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length < settings.CHUNK_SIZE:
                current_chunk += sentence + " "
                current_length += sentence_length
            else:
                # Save current chunk
                if current_chunk.strip():
                    chunks.append(Chunk(
                        text=current_chunk.strip(),
                        metadata={
                            **base_metadata,
                            "chunk_index": len(chunks),
                            "chunk_length": len(current_chunk)
                        }
                    ))

                # Start new chunk with overlap
                overlap_size = settings.CHUNK_OVERLAP
                overlap_text = current_chunk[-overlap_size:] if len(current_chunk) > overlap_size else current_chunk
                current_chunk = overlap_text + sentence + " "
                current_length = len(current_chunk)

        # Add last chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                text=current_chunk.strip(),
                metadata={
                    **base_metadata,
                    "chunk_index": len(chunks),
                    "chunk_length": len(current_chunk)
                }
            ))

        return chunks

# Singleton instance
document_processor = DocumentProcessor()
```

### **1.7 Create `backend/app/services/vector_store.py`**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
import uuid
from ..core.config import settings

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if settings.QDRANT_COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {settings.QDRANT_COLLECTION_NAME}")

    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Insert or update chunks with embeddings"""
        points = []

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "metadata": chunk["metadata"]
                }
            )
            points.append(point)

        self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points
        )

        return len(points)

    def search(self, query_embedding: List[float], document_id: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        if limit is None:
            limit = settings.TOP_K_RESULTS

        # Build filter
        search_filter = None
        if document_id:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="metadata.document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )

        # Perform search
        results = self.client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=limit,
            score_threshold=settings.SIMILARITY_THRESHOLD
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result.payload["text"],
                "metadata": result.payload["metadata"],
                "score": result.score
            })

        return formatted_results

    def delete_by_document(self, document_id: str):
        """Delete all chunks for a document"""
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        self.client.delete(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="metadata.document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
        )

# Singleton instance
vector_store = VectorStore()
```

### **1.8 Create `backend/app/services/llm.py`**

```python
from groq import Groq
from typing import List, Dict, Any
from ..core.config import settings

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.DEFAULT_LLM_MODEL

    async def generate_answer(self, context: str, question: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate answer using LLM with context
        """
        # Build system prompt
        system_prompt = """You are a helpful AI assistant that answers questions based ONLY on the provided context from documents.

Key instructions:
1. ONLY use information from the given context
2. If the answer is not in the context, say "I don't have enough information to answer this question based on the provided documents."
3. Cite sources for every major claim using the format: [Source: {filename}, Page {page}]
4. Be concise but comprehensive
5. If multiple sources provide information, synthesize them
6. Never make up information not in the context

Response format:
- Provide a direct answer first
- Support with details from the context
- Include source citations inline"""

        # Build user prompt
        user_prompt = f"""Context from documents:

{context}

Question: {question}

Please provide a well-sourced answer based on the context above."""

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges

        # Add current query
        messages.append({"role": "user", "content": user_prompt})

        # Call LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=1000,
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"LLM error: {e}")
            return f"Error generating response: {str(e)}"

# Singleton instance
llm_service = LLMService()
```

### **1.9 Create `backend/app/services/rag.py`**

```python
from typing import List, Dict, Any
from .embeddings import embedding_service
from .vector_store import vector_store
from .llm import llm_service

class RAGService:

    async def query(
        self,
        question: str,
        document_id: str = None,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve context and generate answer
        """

        # Step 1: Embed the question
        question_embedding = embedding_service.embed_text(question)

        # Step 2: Retrieve relevant chunks
        relevant_chunks = vector_store.search(
            query_embedding=question_embedding,
            document_id=document_id
        )

        if not relevant_chunks:
            return {
                "answer": "I couldn't find any relevant information in the documents to answer your question.",
                "sources": [],
                "context_used": ""
            }

        # Step 3: Construct context
        context_parts = []
        for idx, chunk in enumerate(relevant_chunks, 1):
            metadata = chunk["metadata"]
            source_info = f"[Document: {metadata.get('filename', 'Unknown')}"
            if metadata.get('page'):
                source_info += f", Page {metadata['page']}"
            source_info += "]"

            context_parts.append(f"{source_info}\n{chunk['text']}\n")

        context = "\n---\n".join(context_parts)

        # Step 4: Generate answer using LLM
        answer = await llm_service.generate_answer(
            context=context,
            question=question,
            conversation_history=conversation_history
        )

        # Step 5: Format sources
        sources = []
        for chunk in relevant_chunks:
            metadata = chunk["metadata"]
            sources.append({
                "document_id": metadata.get("document_id"),
                "filename": metadata.get("filename"),
                "page": metadata.get("page"),
                "chunk_text": chunk["text"][:200] + "...",  # Preview
                "relevance_score": round(chunk["score"], 3)
            })

        return {
            "answer": answer,
            "sources": sources,
            "context_used": context
        }

# Singleton instance
rag_service = RAGService()
```

---

_[Continued in next message due to length...]_

Would you like me to continue with:

1. API endpoints (routes)
2. Frontend implementation
3. Docker setup
4. Deployment configuration

Or would you prefer to start implementing the backend first and get it working before moving to the frontend?
