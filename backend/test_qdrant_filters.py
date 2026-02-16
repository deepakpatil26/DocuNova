from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.config import settings
from app.services.embeddings import embedding_service

client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

def test_filters(doc_id):
    test_query = "readme"
    embedding = embedding_service.embed_text(test_query)
    
    print(f"\n--- TESTING FILTERS FOR doc_id: {doc_id} ---")
    
    # Style 1: Dot notation metadata.document_id
    f1 = Filter(must=[FieldCondition(key="metadata.document_id", match=MatchValue(value=doc_id))])
    res1 = client.query_points(collection_name=settings.QDRANT_COLLECTION_NAME, query=embedding, query_filter=f1, limit=3).points
    print(f"Style 1 (metadata.document_id): Found {len(res1)} points")

    # Style 2: Direct match dict
    f2 = Filter(must=[FieldCondition(key="metadata", match=MatchValue(value={"document_id": doc_id}))])
    try:
        res2 = client.query_points(collection_name=settings.QDRANT_COLLECTION_NAME, query=embedding, query_filter=f2, limit=3).points
        print(f"Style 2 (match object in metadata): Found {len(res2)} points")
    except Exception as e:
        print(f"Style 2 Failed: {e}")

    # Style 3: Search without filter but filter results in python to check score
    res3 = client.query_points(collection_name=settings.QDRANT_COLLECTION_NAME, query=embedding, limit=10).points
    matches = [r for r in res3 if r.payload.get('metadata', {}).get('document_id') == doc_id]
    print(f"Style 3 (No filter search, python match): Found {len(matches)} matches in top 10")
    for m in matches:
        print(f"  Score: {m.score:.4f} | Text: {m.payload['text'][:30]}...")

try:
    print(f"Collection: {settings.QDRANT_COLLECTION_NAME}")
    points = client.scroll(collection_name=settings.QDRANT_COLLECTION_NAME, limit=1, with_payload=True)[0]
    if points:
        doc_id = points[0].payload.get('metadata', {}).get('document_id')
        print(f"Retrieved sample doc_id: {doc_id}")
        test_filters(doc_id)
    else:
        print("Empty collection.")
except Exception as e:
    print(f"Error: {e}")
