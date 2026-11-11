"""
Provider factories and exports.
"""

from typing import Optional
from .base import LLMProvider, clean_json_text
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .mock_provider import MockProvider

__all__ = [
    "LLMProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "MockProvider",
    "clean_json_text",
    "get_provider",
]


def get_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
) -> LLMProvider:
    """
    Factory function returning the configured LLM provider instance.
    """
    p_name = provider_name.lower().strip()
    if p_name in ["gemini", "google"]:
        model = model_name or "gemini-2.5-flash"
        return GeminiProvider(api_key=api_key, model_name=model)
    elif p_name in ["openai", "chatgpt"]:
        model = model_name or "gpt-4o-mini"
        return OpenAIProvider(api_key=api_key, model_name=model)
    elif p_name in ["mock", "test", "offline"]:
        model = model_name or "mock-model"
        return MockProvider(api_key=api_key, model_name=model)
    else:
        raise ValueError(
            f"Unsupported provider: '{provider_name}'. Must be one of 'gemini', 'openai', or 'mock'."
        )
