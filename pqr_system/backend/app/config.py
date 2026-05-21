"""
Configuration settings for the PQR System.
Uses pydantic-settings for environment variable management.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(default="sk-placeholder", alias="PQR_OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="PQR_OPENAI_BASE_URL")
    openai_classification_model: str = Field(default="gpt-4", alias="PQR_OPENAI_CLASSIFICATION_MODEL")
    openai_model: str = Field(default="gpt-4", alias="PQR_OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-ada-002", alias="PQR_OPENAI_EMBEDDING_MODEL"
    )

    # Application Settings
    app_name: str = Field(default="Sistema de PQRs - IA", alias="PQR_APP_NAME")
    debug: bool = Field(default=True, alias="PQR_DEBUG")
    host: str = Field(default="0.0.0.0", alias="PQR_HOST")
    port: int = Field(default=8000, alias="PQR_PORT")

    # ChromaDB Settings
    chroma_persist_dir: str = Field(
        default="./data/chroma_db", alias="PQR_CHROMA_PERSIST_DIR"
    )
    chroma_collection_name: str = Field(
        default="pqr_knowledge_base", alias="PQR_CHROMA_COLLECTION_NAME"
    )

    # PQR Settings
    default_entity_name: str = Field(
        default="Entidad Pública Colombiana", alias="PQR_DEFAULT_ENTITY_NAME"
    )
    default_entity_nit: str = Field(
        default="900000000-1", alias="PQR_DEFAULT_ENTITY_NIT"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()