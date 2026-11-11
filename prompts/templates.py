"""
Parameterized prompt template engine for structured document extraction.
"""

from typing import Any, Dict, List, Optional
import json


SYSTEM_PROMPT = """You are an advanced, enterprise-grade document extraction AI.
Your objective is to extract structured information from messy, unstructured text documents (such as invoices, receipts, and resumes/CVs) with 100% precision.

CRITICAL INSTRUCTIONS:
1. Return ONLY valid, RFC 8259 compliant JSON matching the requested schema.
2. Do NOT include markdown formatting or commentary outside the JSON object unless code fences are explicitly handled.
3. Every required field must be populated. If an optional field is missing or cannot be inferred from the document text, use `null` (None) or an empty array `[]` as indicated by the schema.
4. Normalize and clean data:
   - Strip leading/trailing whitespace.
   - For monetary amounts, extract numbers as floats without currency symbols (e.g. 1250.50 instead of "$1,250.50").
   - Standardize dates to ISO format (YYYY-MM-DD or YYYY-MM) whenever possible.
   - For line items or experiences, capture all entries present in the document.
5. Adhere strictly to the provided Pydantic JSON schema specification.
"""


INVOICE_EXTRACTION_TEMPLATE = """You are tasked with extracting all relevant invoice data from the following unstructured document text into a validated JSON structure.

--- TARGET JSON SCHEMA ---
{schema_json}

--- SPECIAL EXTRACTION RULES ---
- Vendor: Extract the issuing company's name, address, tax ID/VAT, email, phone, and website.
- Customer: Extract the client/buyer information.
- Line Items: Extract each product or service with item code (if any), description, quantity, unit price, and total price. Ensure numeric values are numbers, not strings with currency symbols.
- Financial Totals: Reconcile subtotal, discounts, taxes, shipping, and grand total. Ensure that grand total accurately reflects the items.
- Payment Details: Extract payment terms (e.g. 'Net 30'), due date, bank details, and payment status.
{additional_instructions}

{few_shot_section}

--- DOCUMENT TEXT TO EXTRACT ---
```text
{document_text}
```

Now, output the final extracted JSON object:"""


RESUME_EXTRACTION_TEMPLATE = """You are tasked with extracting structured candidate data from the following unstructured resume/CV text into a validated JSON structure.

--- TARGET JSON SCHEMA ---
{schema_json}

--- SPECIAL EXTRACTION RULES ---
- Contact Info: Extract full name, email, phone number, location, and profiles (LinkedIn, GitHub, Portfolio).
- Summary: Extract the professional summary or objective if present.
- Work Experience: For every employment position, extract job title, company name, location, date range (start date, end date, is_current), bulleted responsibilities/achievements, and technologies used.
- Education: Extract degree, institution, graduation year, GPA, and honors.
- Skills: Categorize skills into logical groups (e.g. 'Languages', 'Frameworks & Libraries', 'Databases', 'Cloud & DevOps', 'Tools', 'Soft Skills').
- Projects & Certifications: Extract any independent projects and professional certifications.
{additional_instructions}

{few_shot_section}

--- DOCUMENT TEXT TO EXTRACT ---
```text
{document_text}
```

Now, output the final extracted JSON object:"""


def format_few_shot_examples(examples: List[Dict[str, Any]]) -> str:
    """Format few-shot examples into readable prompt sections."""
    if not examples:
        return ""

    sections = ["--- FEW-SHOT DEMONSTRATION EXAMPLES ---"]
    for idx, eg in enumerate(examples, 1):
        sections.append(f"### Example {idx} Input:\n```text\n{eg['input_text']}\n```")
        sections.append(f"### Example {idx} Expected JSON Output:\n```json\n{json.dumps(eg['expected_output'], indent=2)}\n```\n")
    return "\n\n".join(sections)


class ExtractionPromptBuilder:
    """
    Parameterized prompt builder for dynamic prompt construction.
    """

    def __init__(
        self,
        document_type: str,
        schema: Any,
        few_shot_examples: Optional[List[Dict[str, Any]]] = None,
        additional_instructions: Optional[str] = None,
    ):
        self.document_type = document_type.lower()
        self.schema = schema
        self.few_shot_examples = few_shot_examples or []
        self.additional_instructions = additional_instructions or ""

    def build_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def build_user_prompt(self, document_text: str) -> str:
        schema_json = json.dumps(self.schema.model_json_schema(), indent=2)
        few_shot_section = format_few_shot_examples(self.few_shot_examples)
        extra_inst = f"- Additional Notes: {self.additional_instructions}" if self.additional_instructions else ""

        if self.document_type == "invoice":
            template = INVOICE_EXTRACTION_TEMPLATE
        elif self.document_type in ["resume", "cv"]:
            template = RESUME_EXTRACTION_TEMPLATE
        else:
            raise ValueError(f"Unsupported document type: {self.document_type}. Supported: 'invoice', 'resume'")

        return template.format(
            schema_json=schema_json,
            few_shot_section=few_shot_section,
            additional_instructions=extra_inst,
            document_text=document_text.strip(),
        )
