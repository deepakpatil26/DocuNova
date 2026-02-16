from app.services.document_processor import DocumentProcessor

def test_smart_chunk_text():
    document_id = "test-doc-id"
    filename = "test.txt"
    metadata = {"total_pages": 1}
    
    # Create a text slightly larger than CHUNK_SIZE (1000) to force chunking
    # 1200 characters
    long_text = "This is a sentence. " * 60 
    
    chunks = DocumentProcessor.smart_chunk(
        text=long_text,
        document_id=document_id,
        filename=filename,
        metadata=metadata
    )
    
    assert len(chunks) > 0
    # Ideally should be at least 2 chunks
    assert len(chunks) >= 2
    
    # Check if metadata is preserved
    assert chunks[0].metadata["document_id"] == document_id
    assert chunks[0].metadata["filename"] == filename
