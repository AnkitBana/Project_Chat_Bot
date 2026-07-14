"""
LLM Provider abstraction — supports OpenAI, Anthropic, Google, and ICA.
"""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel
from config import settings, validate_api_keys


class LLMProvider:
    """Factory for creating LLM instances."""

    @staticmethod
    def get_llm(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> BaseChatModel:
        """Return a configured LLM instance."""
        provider = provider or settings.default_llm_provider
        temperature = temperature if temperature is not None else settings.temperature
        validate_api_keys()

        if provider == "openai":
            return ChatOpenAI(
                model=model or settings.openai_model,
                temperature=temperature,
                api_key=settings.openai_api_key,
                **kwargs,
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=model or settings.anthropic_model,
                temperature=temperature,
                api_key=settings.anthropic_api_key,
                **kwargs,
            )
        elif provider == "google":
            return ChatGoogleGenerativeAI(
                model=model or settings.google_model,
                temperature=temperature,
                google_api_key=settings.google_api_key,
                **kwargs,
            )
        elif provider == "ica":
            # ICA (IBM Cognitive Architecture) uses its own API key (ak_...) directly
            # as a Bearer token — no IAM token exchange needed.
            # The endpoint is OpenAI-compatible at /v1.
            api_key  = settings.ica_api_key
            base_url = settings.ica_base_url.rstrip("/")
            return ChatOpenAI(
                model=model or settings.ica_model,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url,
                default_headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                },
                **kwargs,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def get_available_providers() -> dict:
        return {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key),
            "google": bool(settings.google_api_key),
            "ica": bool(settings.ica_api_key),
        }

    @staticmethod
    def get_provider_info(provider: Optional[str] = None) -> dict:
        provider = provider or settings.default_llm_provider
        model_map = {
            "openai": settings.openai_model,
            "anthropic": settings.anthropic_model,
            "google": settings.google_model,
            "ica": settings.ica_model,
        }
        key_map = {
            "openai": settings.openai_api_key,
            "anthropic": settings.anthropic_api_key,
            "google": settings.google_api_key,
            "ica": settings.ica_api_key,
        }
        return {
            "provider": provider,
            "model": model_map.get(provider),
            "available": bool(key_map.get(provider, "")),
        }
