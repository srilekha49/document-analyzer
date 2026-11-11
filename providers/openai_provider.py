"""
OpenAI API provider implementation with structured output enforcement.
"""

import os
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from .base import LLMProvider, clean_json_text

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    """
    Provider for OpenAI models (GPT-4o, GPT-4o-mini).
    Uses native Pydantic structured outputs via client.beta.chat.completions.parse.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY in your environment, .env file, or pass --api-key."
            )
        super().__init__(api_key=resolved_key, model_name=model_name)
        self._init_client()

    def _init_client(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError as e:
            raise ImportError("OpenAI package not installed. Install with: pip install openai") from e

    def generate_raw(self, system_prompt: str, user_prompt: str, target_schema: Type[T]) -> str:
        """
        Sends request to OpenAI Chat Completion with structured outputs or JSON mode.
        """
        try:
            # Try native Pydantic structured output parsing
            completion = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=target_schema,
                temperature=0.1,
            )
            # If parsed successfully by OpenAI SDK
            message = completion.choices[0].message
            if hasattr(message, "parsed") and message.parsed is not None:
                return message.parsed.model_dump_json()
            return message.content or ""
        except Exception:
            # Fallback to standard json_object mode
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            return completion.choices[0].message.content or ""
