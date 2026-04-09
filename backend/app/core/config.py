"""
app/core/config.py
Centralised settings loaded from environment / .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.2

    # OpenAI embeddings (still needed for ChromaDB)
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    # Database
    database_url: str = "sqlite:///./reports.db"

    # ChromaDB
    chroma_collection_name: str = "medical_documents"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()
