from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import re
import hashlib
from ..core.config import settings

class EmbeddingService:
    def __init__(self):
        # Initialize with a lightweight model by default to avoid large downloads during dev
        self.model_name = settings.EMBEDDING_MODEL
        self._model = None
        self._use_fallback = False

    @property
    def model(self):
        if self._use_fallback:
            return None
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}...")
            try:
                self._model = SentenceTransformer(
                    self.model_name,
                    local_files_only=settings.EMBEDDING_LOCAL_FILES_ONLY
                )
                print("Embedding model loaded.")
            except Exception as e:
                print(f"Embedding model load failed, using fallback embeddings: {e}")
                self._use_fallback = True
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
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if self.model is None:
            return [self._fallback_embed_text(t) for t in texts]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get embedding dimension"""
        if self.model is None:
            return settings.EMBEDDING_DIMENSION
        return self.model.get_sentence_embedding_dimension()

# Singleton instance
embedding_service = EmbeddingService()
