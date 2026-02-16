from qdrant_client import QdrantClient
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.config import settings
from app.services.embeddings import embedding_service

client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

print(f"Checking collection: {settings.QDRANT_COLLECTION_NAME}")
try:
    count = client.count(collection_name=settings.QDRANT_COLLECTION_NAME).count
    print(f"Total points in collection: {count}")

    # 1. Inspect Payload Structure
    points = client.scroll(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        limit=1,
        with_payload=True
    )[0]
    
    if points:
        p = points[0]
        print(f"\n--- Payload Sample (ID: {p.id}) ---")
        import json
        print(json.dumps(p.payload, indent=2))
    else:
        print("No points found in collection.")

    # 2. Test Search without Filter
    test_query = "readme"
    embedding = embedding_service.embed_text(test_query)
    
    print(f"\n--- Search Test (Query: '{test_query}', No Filter, No Threshold) ---")
    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        query=embedding,
        limit=5
    ).points
    
    for r in results:
        print(f"Score: {r.score:.4f} | DocID: {r.payload.get('metadata', {}).get('document_id')} | Preview: {r.payload.get('text', '')[:50]}")

    # 3. Test Search WITH Filter
    # Get a doc_id from the sample
    if points:
        doc_id = points[0].payload.get('metadata', {}).get('document_id')
        if doc_id:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            print(f"\n--- Search Test (With Filter: document_id={doc_id}) ---")
            results_filtered = client.query_points(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query=embedding,
                query_filter=Filter(
                    must=[FieldCondition(key="metadata.document_id", match=MatchValue(value=doc_id))]
                ),
                limit=5
            ).points
            print(f"Found {len(results_filtered)} results with filter.")
            for r in results_filtered:
                print(f"Score: {r.score:.4f} | Preview: {r.payload.get('text', '')[:50]}")

except Exception as e:
    import traceback
    traceback.print_exc()
