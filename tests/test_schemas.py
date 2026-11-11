"""
Unit tests for Pydantic schemas, prompt builders, and extraction pipelines.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import ValidationError
from schemas.invoice import Invoice, LineItem, VendorInfo, CustomerInfo
from schemas.resume import (
    Resume,
    ContactInfo,
    EducationEntry,
    ExperienceEntry,
    SkillCategory,
)
from prompts.templates import ExtractionPromptBuilder
from prompts.few_shot_examples import INVOICE_FEW_SHOT_EXAMPLES, RESUME_FEW_SHOT_EXAMPLES
from providers.mock_provider import MockProvider
from providers.base import clean_json_text


def test_invoice_schema_valid():
    invoice = Invoice(
        invoice_number="INV-001",
        invoice_date="2024-01-15",
        currency="$",
        vendor=VendorInfo(name="Acme Corp"),
        customer=CustomerInfo(name="Globex Inc"),
        line_items=[
            LineItem(
                description="Consulting",
                quantity=10,
                unit_price=100.0,
                total_price=1000.0,
            )
        ],
        subtotal=1000.0,
        discount_total=50.0,
        tax_total=80.0,
        shipping_fee=0.0,
        grand_total=1030.0,
    )
    assert invoice.currency == "USD"
    assert invoice.grand_total == 1030.0
    assert len(invoice.line_items) == 1
    print("✓ test_invoice_schema_valid passed")


def test_invoice_financial_mismatch_raises_error():
    try:
        Invoice(
            invoice_number="INV-002",
            invoice_date="2024-01-15",
            vendor=VendorInfo(name="Acme Corp"),
            customer=CustomerInfo(name="Globex Inc"),
            line_items=[
                LineItem(
                    description="Consulting",
                    quantity=1,
                    unit_price=100.0,
                    total_price=1000.0,
                )
            ],
            subtotal=100.0,
            discount_total=0.0,
            tax_total=10.0,
            shipping_fee=0.0,
            grand_total=999.0,  # Intentional discrepancy
        )
        assert False, "Should have raised ValidationError for financial mismatch"
    except ValidationError as e:
        assert "Financial mismatch" in str(e)
        print("✓ test_invoice_financial_mismatch_raises_error passed")


def test_resume_schema_valid():
    resume = Resume(
        contact_info=ContactInfo(
            full_name="Jane Doe",
            email="jane.doe@example.com",
            phone="+1-555-0100",
        ),
        professional_summary="Senior Software Engineer with 8 years of experience.",
        education=[
            EducationEntry(
                degree="B.S. in Computer Science",
                institution="MIT",
                graduation_year="2016",
            )
        ],
        work_experience=[
            ExperienceEntry(
                job_title="Lead Architect",
                company="Tech Giant",
                start_date="2020-01",
                end_date="Present",
                is_current=True,
                responsibilities_and_achievements=["Led architecture for 10M users"],
                technologies_used=["Python", "Kubernetes"],
            )
        ],
        skill_categories=[
            SkillCategory(
                category_name="Languages",
                skills=["Python", "Go", "TypeScript"],
            )
        ],
    )
    assert resume.contact_info.full_name == "Jane Doe"
    assert resume.contact_info.email == "jane.doe@example.com"
    assert len(resume.work_experience) == 1
    print("✓ test_resume_schema_valid passed")


def test_prompt_builder():
    builder = ExtractionPromptBuilder(
        document_type="invoice",
        schema=Invoice,
        few_shot_examples=INVOICE_FEW_SHOT_EXAMPLES,
        additional_instructions="Strictly extract dates as ISO-8601.",
    )
    system_prompt = builder.build_system_prompt()
    user_prompt = builder.build_user_prompt("Invoice # 123 from Acme...")

    assert "TARGET JSON SCHEMA" in user_prompt
    assert "FEW-SHOT DEMONSTRATION EXAMPLES" in user_prompt
    assert "Invoice # 123 from Acme..." in user_prompt
    assert "Strictly extract dates as ISO-8601." in user_prompt
    assert "RFC 8259" in system_prompt
    print("✓ test_prompt_builder passed")


def test_clean_json_text():
    markdown_wrapped = """Here is the result:
```json
{
    "invoice_number": "INV-123",
    "grand_total": 450.0
}
```
Hope this helps!"""
    cleaned = clean_json_text(markdown_wrapped)
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")
    assert '"invoice_number": "INV-123"' in cleaned
    print("✓ test_clean_json_text passed")


def test_mock_provider_invoice_extraction():
    provider = MockProvider()
    builder = ExtractionPromptBuilder(document_type="invoice", schema=Invoice)
    system_prompt = builder.build_system_prompt()
    user_prompt = builder.build_user_prompt("Sample raw invoice text")

    extracted = provider.extract(system_prompt, user_prompt, Invoice)
    assert isinstance(extracted, Invoice)
    assert extracted.invoice_number == "INV-2024-9982"
    assert extracted.grand_total == 17320.0
    assert len(extracted.line_items) == 3
    print("✓ test_mock_provider_invoice_extraction passed")


def test_mock_provider_resume_extraction():
    provider = MockProvider()
    builder = ExtractionPromptBuilder(document_type="resume", schema=Resume)
    system_prompt = builder.build_system_prompt()
    user_prompt = builder.build_user_prompt("Sample raw resume text")

    extracted = provider.extract(system_prompt, user_prompt, Resume)
    assert isinstance(extracted, Resume)
    assert extracted.contact_info.full_name == "Samantha K. Reed"
    assert len(extracted.work_experience) == 2
    print("✓ test_mock_provider_resume_extraction passed")


if __name__ == "__main__":
    print("Running test suite...\n")
    test_invoice_schema_valid()
    test_invoice_financial_mismatch_raises_error()
    test_resume_schema_valid()
    test_prompt_builder()
    test_clean_json_text()
    test_mock_provider_invoice_extraction()
    test_mock_provider_resume_extraction()
    print("\nAll 7 test cases executed successfully!")
