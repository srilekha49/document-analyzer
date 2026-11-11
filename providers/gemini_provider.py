"""
Google Gemini API provider implementation with structured output enforcement.
"""

import os
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from .base import LLMProvider, clean_json_text

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LLMProvider):
    """
    Provider for Google Gemini models using the modern google-genai SDK.
    Supports native schema enforcement via response_schema and JSON mode.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        resolved_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not resolved_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY in your environment, .env file, or pass --api-key."
            )
        super().__init__(api_key=resolved_key, model_name=model_name)
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self._sdk_type = "genai"
        except ImportError:
            # Fallback to legacy google.generativeai if installed
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                self.client = legacy_genai
                self._sdk_type = "legacy"
            except ImportError as e:
                raise ImportError(
                    "Neither 'google-genai' nor 'google-generativeai' is installed. "
                    "Install with: pip install google-genai"
                ) from e

    def generate_raw(self, system_prompt: str, user_prompt: str, target_schema: Type[T]) -> str:
        """
        Sends the request to Gemini API with structured response requirements.
        """
        if self._sdk_type == "genai":
            from google.genai import types

            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=target_schema,
                temperature=0.1,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=config,
            )
            return response.text or ""
        else:
            # Legacy google.generativeai
            generation_config = {
                "temperature": 0.1,
                "response_mime_type": "application/json",
            }
            model = self.client.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                system_instruction=system_prompt,
            )
            response = model.generate_content(user_prompt)
            return response.text or ""
