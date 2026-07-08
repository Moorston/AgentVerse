"""Base configuration for all AgentVerse services."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Shared settings, loadable from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""

    postgres_dsn: str = ""

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    cors_origins: list[str] = []