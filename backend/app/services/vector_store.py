from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
import uuid
from ..core.config import settings

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=10 # Add timeout
        )
        # We'll ensure collection on first use to speed up startup
        self._collection_ensured = False

    def ensure_collection(self):
        if not self._collection_ensured:
            self._ensure_collection()
            self._collection_ensured = True

    def _ensure_collection(self):
        """Create collection if it doesn't exist, or recreate if settings mismatch"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if settings.QDRANT_COLLECTION_NAME in collection_names:
                # Check current configuration
                info = self.client.get_collection(collection_name=settings.QDRANT_COLLECTION_NAME)
                vectors_config = info.config.params.vectors
                
                # If distance is not COSINE, we must recreate
                if vectors_config.distance != Distance.COSINE:
                    print(f"Distance mismatch (found {vectors_config.distance}, need COSINE). Recreating collection...")
                    self.client.delete_collection(collection_name=settings.QDRANT_COLLECTION_NAME)
                    collection_names.remove(settings.QDRANT_COLLECTION_NAME)

            if settings.QDRANT_COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {settings.QDRANT_COLLECTION_NAME} with COSINE distance")
        except Exception as e:
            print(f"Error ensuring collection: {e}")

    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Insert or update chunks with embeddings"""
        self.ensure_collection()
        points = []

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Handle chunk object or dict
            text = chunk.text if hasattr(chunk, 'text') else chunk['text']
            metadata = chunk.metadata if hasattr(chunk, 'metadata') else chunk['metadata']

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": text,
                    "metadata": metadata
                }
            )
            points.append(point)

        self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=points
        )

        return len(points)

    def search(self, query_embedding: List[float], document_ids: List[str] = None, user_id: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Search for similar chunks with support for multi-document and user filtering"""
        self.ensure_collection()
        if limit is None:
            limit = settings.TOP_K_RESULTS

        # Build filter
        from qdrant_client.models import Filter, FieldCondition, MatchAny, MatchValue
        
        must_conditions = []
        
        # 1. User Filter (Mandatory for isolation)
        if user_id:
            must_conditions.append(
                FieldCondition(
                    key="metadata.user_id",
                    match=MatchValue(value=str(user_id))
                )
            )
            
        # 2. Document Filters
        if document_ids:
            must_conditions.append(
                FieldCondition(
                    key="metadata.document_id",
                    match=MatchAny(any=[str(d_id) for d_id in document_ids])
                )
            )

        search_filter = Filter(must=must_conditions) if must_conditions else None

        results = []
        # Perform search using query_points (Standard in newer qdrant-client)
        try:
            print(f"DEBUG: Attempting query_points for collection: {settings.QDRANT_COLLECTION_NAME}")
            # Ensure query_embedding is in the right format for query_points (it expects a Query object or raw vector)
            search_result = self.client.query_points(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query=query_embedding,
                query_filter=search_filter,
                limit=limit,
                score_threshold=settings.SIMILARITY_THRESHOLD
            )
            results = search_result.points
        except Exception as e:
            print(f"ERROR: Qdrant query_points failed: {e}")
            raise e

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
        self.ensure_collection()
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
