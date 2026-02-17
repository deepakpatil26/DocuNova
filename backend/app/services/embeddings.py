from fastembed import TextEmbedding
from typing import List
import numpy as np
import re
import hashlib
from ..core.config import settings

class EmbeddingService:
    def __init__(self):
        # fastembed is much faster and doesn't require torch
        self.model_name = "BAAI/bge-small-en-v1.5" # Very fast and efficient
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                print(f"Loading fastembed model: {self.model_name}...")
                self._model = TextEmbedding(model_name=self.model_name)
                print("Fastembed model loaded.")
            except Exception as e:
                print(f"Fastembed model load failed: {e}")
                # Fallback to a simple hash-based embedding if even fastembed fails
                return None
        return self._model

    def _fallback_embed_text(self, text: str) -> List[float]:
        dim = settings.EMBEDDING_DIMENSION
        vec = np.zeros(dim, dtype=np.float32)
        tokens = re.findall(r"\w+", (text or "").lower())
        if not tokens:
            return vec.tolist()

        for tok in tokens:
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
            vec[idx] += sign

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if self.model is None:
            return self._fallback_embed_text(text)
        
        # fastembed.embed returns a generator
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if self.model is None:
            return [self._fallback_embed_text(t) for t in texts]
            
        embeddings = list(self.model.embed(texts))
        return [e.tolist() for e in embeddings]

    def get_dimension(self) -> int:
        """Get embedding dimension"""
        # BAAI/bge-small-en-v1.5 is 384
        return 384

# Singleton instance
embedding_service = EmbeddingService()
