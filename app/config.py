"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Required API keys
    gemini_api_key: str
    scaledown_api_key: str

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/paper_summarizer"

    # Model configuration
    gemini_embedding_model: str = "text-embedding-004"
    gemini_generation_model: str = "gemini-1.5-flash"  # Default, can be overridden by env var

    # ScaleDown configuration
    scaledown_api_url: str = "https://api.scaledown.xyz/compress/raw/"

    # Chunking settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_chunks: int = 5

    # Embedding dimensions (must match model)
    embedding_dimensions: int = 3072


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
