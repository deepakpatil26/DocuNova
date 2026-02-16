from qdrant_client import QdrantClient
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core.config import settings

client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

print(f"Checking collection: {settings.QDRANT_COLLECTION_NAME}")
try:
    count = client.count(collection_name=settings.QDRANT_COLLECTION_NAME).count
    print(f"Total points: {count}")

    if count > 0:
        points = client.scroll(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            limit=5,
            with_payload=True,
            with_vectors=False
        )[0]
        
        print("\nSample points metadata structure:")
        for p in points:
            print(f"ID: {p.id}")
            print(f"Payload keys: {p.payload.keys()}")
            if "metadata" in p.payload:
                print(f"Metadata keys: {p.payload['metadata'].keys()}")
                print(f"Document ID in metadata: {p.payload['metadata'].get('document_id')}")
            print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
