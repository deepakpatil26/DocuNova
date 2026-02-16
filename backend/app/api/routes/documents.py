from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
import shutil
import os
import uuid
import asyncio
from ...core.database import get_db, AsyncSessionLocal
from ...models.document import Document
from ...services.document_processor import document_processor
from ...services.embeddings import embedding_service
from ...services.vector_store import vector_store
from ...core.config import settings
from ...core.auth import current_active_user
from ...models.user import User
from ...core.rate_limit import rate_limiter, Limit

router = APIRouter()

async def process_document_background(file_path: str, document_id: str):
    """Background task to process document with its own DB session"""
    print(f"DEBUG: Starting background processing for document {document_id}")
    async with AsyncSessionLocal() as db:
        try:
            # Convert string ID to UUID object if necessary
            doc_uuid = uuid.UUID(document_id) if isinstance(document_id, str) else document_id
            result = await db.execute(select(Document).filter(Document.id == doc_uuid))
            doc = result.scalar_one_or_none()
            
            if not doc:
                print(f"ERROR: Document {document_id} not found in database during background task")
                return

            print(f"DEBUG: Document found: {doc.filename}. Updating status to 'processing'...")
            doc.processing_status = "processing"
            await db.commit()

            # 1. Extract text
            print(f"DEBUG: Extracting text from {file_path}...")
            if file_path.endswith(".pdf"):
                text, metadata = document_processor.extract_text_from_pdf(file_path)
            else:
                text, metadata = document_processor.extract_text_from_txt(file_path)
            print(f"DEBUG: Text extracted. Length: {len(text)}")

            # Update metadata
            doc.metadata_ = metadata
            doc.total_pages = metadata.get("total_pages", 1)

            # 2. Chunk text
            print(f"DEBUG: Chunking text...")
            chunks = document_processor.smart_chunk(
                text=text,
                document_id=str(document_id),
                filename=doc.filename,
                metadata=metadata
            )
            
            doc.chunk_count = len(chunks)
            print(f"DEBUG: Created {len(chunks)} chunks.")

            # 3. Generate embeddings
            print(f"DEBUG: Generating embeddings for {len(chunks)} chunks...")
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await asyncio.wait_for(
                asyncio.to_thread(embedding_service.embed_batch, chunk_texts),
                timeout=settings.EMBEDDING_TIMEOUT_SECONDS
            )
            print(f"DEBUG: Embeddings generated.")

            # 4. Upsert to Vector Store
            print(f"DEBUG: Upserting to Vector Store...")
            # Add user_id to each chunk's metadata for filtering
            for chunk in chunks:
                chunk.metadata["user_id"] = str(doc.user_id)
                
            vector_store.upsert_chunks(chunks, embeddings)
            print(f"DEBUG: Upsert complete.")

            # Update status
            doc.processing_status = "completed"
            doc.qdrant_collection_id = settings.QDRANT_COLLECTION_NAME
            await db.commit()
            print(f"DEBUG: Processing completed for {doc.filename}")

            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"DEBUG: Temporary file {file_path} removed.")

        except Exception as e:
            print(f"FATAL ERROR processing document {document_id}: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            doc_uuid = uuid.UUID(document_id) if isinstance(document_id, str) else document_id
            result = await db.execute(select(Document).filter(Document.id == doc_uuid))
            doc = result.scalar_one_or_none()
            if doc:
                doc.processing_status = "failed"
                existing_meta = doc.metadata_ or {}
                existing_meta["processing_error"] = str(e)
                doc.metadata_ = existing_meta
                await db.commit()
            if os.path.exists(file_path):
                os.remove(file_path)

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    rate_limiter.hit(f"upload:{user.id}", Limit(max_requests=20, window_seconds=300))

    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {settings.ALLOWED_EXTENSIONS}")

    # Validate file size early to avoid processing oversized uploads
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {settings.MAX_FILE_SIZE} bytes."
        )

    # Create DB entry
    document_id = uuid.uuid4()
    new_doc = Document(
        id=document_id,
        user_id=user.id,
        filename=file.filename,
        original_filename=file.filename,
        file_size=0, # Will update after save
        file_type=file_ext,
        processing_status="pending"
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    # Save file temporarily
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{document_id}{file_ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update file size
    new_doc.file_size = os.path.getsize(file_path)
    await db.commit()

    # Trigger background processing
    background_tasks.add_task(process_document_background, file_path, str(document_id))

    return {
        "id": str(document_id),
        "filename": new_doc.filename,
        "status": "upload_success_processing_started"
    }


@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    doc_uuid = uuid.UUID(document_id) if isinstance(document_id, str) else document_id
    result = await db.execute(
        select(Document).filter(Document.id == doc_uuid, Document.user_id == user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "original_filename": doc.original_filename,
        "upload_date": doc.upload_date,
        "status": doc.processing_status,
        "chunk_count": doc.chunk_count,
        "file_size": doc.file_size,
        "file_type": doc.file_type,
        "total_pages": doc.total_pages,
        "qdrant_collection_id": doc.qdrant_collection_id,
        "metadata": doc.metadata_ or {}
    }

@router.get("/", response_model=List[dict])
@router.get("", response_model=List[dict])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    result = await db.execute(
        select(Document)
        .filter(Document.user_id == user.id)
        .order_by(Document.upload_date.desc())
    )
    docs = result.scalars().all()
    return [
        {
            "id": str(doc.id),
            "filename": doc.filename,
            "upload_date": doc.upload_date,
            "status": doc.processing_status,
            "chunk_count": doc.chunk_count,
            "file_size": doc.file_size
        }
        for doc in docs
    ]

@router.delete("/{document_id}")
async def delete_document(
    document_id: str, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    doc_uuid = uuid.UUID(document_id) if isinstance(document_id, str) else document_id
    result = await db.execute(
        select(Document).filter(Document.id == doc_uuid, Document.user_id == user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from Qdrant
    vector_store.delete_by_document(document_id)

    # Delete from DB
    await db.delete(doc)
    await db.commit()

    return {"message": "Document deleted successfully"}
