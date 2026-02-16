from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.config import settings

client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

try:
    print(f"Collection: {settings.QDRANT_COLLECTION_NAME}")
    
    # 1. Try filter by filename
    points = client.scroll(collection_name=settings.QDRANT_COLLECTION_NAME, limit=1, with_payload=True)[0]
    if points:
        filename = points[0].payload.get('metadata', {}).get('filename')
        doc_id = points[0].payload.get('metadata', {}).get('document_id')
        print(f"Sample: filename={filename}, doc_id={doc_id}")
        
        print("\n--- Testing Filename Filter ---")
        f_name = Filter(must=[FieldCondition(key="metadata.filename", match=MatchValue(value=filename))])
        res_name = client.query_points(collection_name=settings.QDRANT_COLLECTION_NAME, query=[0.0]*settings.EMBEDDING_DIMENSION, query_filter=f_name, limit=5).points
        print(f"Filename filter found {len(res_name)} points")

        print("\n--- Testing doc_id Filter again (Exact string) ---")
        f_id = Filter(must=[FieldCondition(key="metadata.document_id", match=MatchValue(value=str(doc_id)))])
        res_id = client.query_points(collection_name=settings.QDRANT_COLLECTION_NAME, query=[0.0]*settings.EMBEDDING_DIMENSION, query_filter=f_id, limit=5).points
        print(f"doc_id filter found {len(res_id)} points")

        print("\n--- Raw Scroll with Filter ---")
        res_scroll = client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            scroll_filter=f_id,
            limit=5
        )[0]
        print(f"Scroll with doc_id filter found {len(res_scroll)} points")

    else:
        print("Empty collection.")
except Exception as e:
    import traceback
    traceback.print_exc()
