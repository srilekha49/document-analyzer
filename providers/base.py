"""
Base provider abstraction and JSON parsing utilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar
import json
import re
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def clean_json_text(text: str) -> str:
    """
    Cleans raw LLM response text by stripping Markdown backticks,
    whitespace, and isolating the primary JSON structure.
    """
    cleaned = text.strip()

    # Match ```json ... ``` or ``` ... ```
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if code_block_match:
        cleaned = code_block_match.group(1).strip()

    # Find the first '{' and last '}'
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace : last_brace + 1]

    return cleaned


class LLMProvider(ABC):
    """Abstract base class for document extraction LLM providers."""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def generate_raw(self, system_prompt: str, user_prompt: str, target_schema: Type[T]) -> str:
        """Invokes the LLM and returns the raw text output."""
        pass

    def extract(
        self,
        system_prompt: str,
        user_prompt: str,
        target_schema: Type[T],
    ) -> T:
        """
        Executes prompt, cleans the returned response, and validates it against the Pydantic schema.
        """
        raw_output = self.generate_raw(system_prompt, user_prompt, target_schema)
        cleaned_json = clean_json_text(raw_output)

        try:
            # Enforce strict validation
            validated_instance = target_schema.model_validate_json(cleaned_json)
            return validated_instance
        except (ValidationError, json.JSONDecodeError) as e:
            raise ValueError(
                f"Failed to validate extracted JSON against {target_schema.__name__} schema.\n"
                f"Error: {e}\n"
                f"Cleaned Output was:\n{cleaned_json}"
            ) from e
