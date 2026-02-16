from pydantic_settings import BaseSettings
from typing import Optional, List, Set, Union
import os
import json

class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "DocuChat"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Qdrant Vector Database
    QDRANT_URL: str
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "documents"

    # LLM Configuration
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "llama-3.3-70b-versatile"  # Groq model

    # Embedding Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_LOCAL_FILES_ONLY: bool = True
    EMBEDDING_TIMEOUT_SECONDS: int = 90

    # Document Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".txt", ".md"}
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # RAG Configuration
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

    # Authentication
    SECRET_KEY: str = "8cc683796856012ccfac39f72b64d1894b95f2e633d659ad125f46487e915478"
    JWT_SECRET: str = "8cc683796856012ccfac39f72b64d1894b95f2e633d659ad125f46487e915478"
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    ADMIN_EMAILS: Union[List[str], str] = ["admin@gmail.com"]

    # Sentry (optional)
    SENTRY_DSN: Optional[str] = None

    # Firebase Admin (optional)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_CREDENTIALS_JSON: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.ALLOWED_ORIGINS, str):
            try:
                return json.loads(self.ALLOWED_ORIGINS)
            except json.JSONDecodeError:
                return [self.ALLOWED_ORIGINS]
        return self.ALLOWED_ORIGINS

    @property
    def admin_emails(self) -> List[str]:
        if isinstance(self.ADMIN_EMAILS, str):
            try:
                value = json.loads(self.ADMIN_EMAILS)
                return [v.lower() for v in value] if isinstance(value, list) else [self.ADMIN_EMAILS.lower()]
            except json.JSONDecodeError:
                return [self.ADMIN_EMAILS.lower()]
        return [v.lower() for v in self.ADMIN_EMAILS]

settings = Settings()
