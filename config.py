"""
Configuration management for the AI Agent system.
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider Configuration
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")

    default_llm_provider: Literal["openai", "anthropic", "google"] = Field(
        default="openai", alias="DEFAULT_LLM_PROVIDER"
    )

    # Model Configuration
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    anthropic_model: str = Field(default="claude-3-5-haiku-20241022", alias="ANTHROPIC_MODEL")
    google_model: str = Field(default="gemini-2.5-flash-lite", alias="GOOGLE_MODEL")

    temperature: float = Field(default=0.7, alias="TEMPERATURE")
    max_tokens: int = Field(default=4096, alias="MAX_TOKENS")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "populate_by_name": True}


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    return settings


def validate_api_keys():
    """Validate that the required API key for the chosen provider is set."""
    provider = settings.default_llm_provider
    if provider == "openai" and not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
    elif provider == "anthropic" and not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
    elif provider == "google" and not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is required when using Google provider")


def setup_directories():
    """Create necessary data directories."""
    for path in ["./data/memory", "./data/files", "./logs"]:
        os.makedirs(path, exist_ok=True)
