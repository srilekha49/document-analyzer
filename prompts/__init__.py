"""
Prompt generation and template management.
"""

from .templates import SYSTEM_PROMPT, ExtractionPromptBuilder
from .few_shot_examples import INVOICE_FEW_SHOT_EXAMPLES, RESUME_FEW_SHOT_EXAMPLES

__all__ = [
    "SYSTEM_PROMPT",
    "ExtractionPromptBuilder",
    "INVOICE_FEW_SHOT_EXAMPLES",
    "RESUME_FEW_SHOT_EXAMPLES",
]
