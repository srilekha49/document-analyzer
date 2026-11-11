#!/usr/bin/env python3
"""
Document Analyzer CLI: LLM-powered extraction with Parameterized Prompts & Pydantic Validation.
Supports Google Gemini, OpenAI, and Mock/Offline execution.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from schemas.invoice import Invoice
from schemas.resume import Resume
from prompts.templates import ExtractionPromptBuilder
from prompts.few_shot_examples import INVOICE_FEW_SHOT_EXAMPLES, RESUME_FEW_SHOT_EXAMPLES
from providers import get_provider


BASE_DIR = Path(__file__).parent
SAMPLES_DIR = BASE_DIR / "samples"


def detect_provider(requested_provider: str) -> str:
    """Auto-detect provider based on available environment variables if not specified."""
    if requested_provider != "auto":
        return requested_provider

    env_default = os.environ.get("DEFAULT_LLM_PROVIDER")
    if env_default:
        return env_default.lower()

    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    elif os.environ.get("OPENAI_API_KEY"):
        return "openai"
    else:
        # Default to mock with an informative warning
        return "mock"


def run_pipeline(
    document_type: str,
    file_path: Optional[str] = None,
    provider_name: str = "auto",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    use_few_shot: bool = True,
    output_path: Optional[str] = None,
    show_prompt: bool = False,
) -> None:
    doc_type = document_type.lower()
    if doc_type not in ["invoice", "resume"]:
        print(f"[-] Error: Document type '{doc_type}' is unsupported. Choose 'invoice' or 'resume'.")
        sys.exit(1)

    # 1. Resolve Document Text
    if file_path:
        path = Path(file_path)
        if not path.is_file():
            print(f"[-] Error: Input file '{file_path}' does not exist.")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            document_text = f.read()
        source_label = str(path)
    else:
        sample_file = SAMPLES_DIR / f"sample_{doc_type}_complex.txt"
        if not sample_file.is_file():
            print(f"[-] Error: Default sample file '{sample_file}' not found.")
            sys.exit(1)
        with open(sample_file, "r", encoding="utf-8") as f:
            document_text = f.read()
        source_label = f"Built-in complex sample ({sample_file.name})"

    # 2. Select Schema & Few-Shot Examples
    if doc_type == "invoice":
        target_schema = Invoice
        few_shots = INVOICE_FEW_SHOT_EXAMPLES if use_few_shot else []
    else:
        target_schema = Resume
        few_shots = RESUME_FEW_SHOT_EXAMPLES if use_few_shot else []

    # 3. Construct Parameterized Prompt
    prompt_builder = ExtractionPromptBuilder(
        document_type=doc_type,
        schema=target_schema,
        few_shot_examples=few_shots,
    )
    system_prompt = prompt_builder.build_system_prompt()
    user_prompt = prompt_builder.build_user_prompt(document_text)

    if show_prompt:
        print("\n" + "=" * 80)
        print("--- SYSTEM PROMPT ---")
        print(system_prompt)
        print("\n--- USER PROMPT ---")
        print(user_prompt)
        print("=" * 80 + "\n")
        return

    # 4. Resolve Provider
    resolved_provider = detect_provider(provider_name)
    print("=" * 70)
    print("           DOCUMENT EXTRACTION & VALIDATION PIPELINE           ")
    print("=" * 70)
    print(f"  • Target Schema:   {target_schema.__name__}")
    print(f"  • Source Document: {source_label}")
    print(f"  • Provider:        {resolved_provider.upper()}")
    print(f"  • Few-Shot Active: {use_few_shot} ({len(few_shots)} example(s))")

    if resolved_provider == "mock" and provider_name == "auto":
        print("\n  [!] NOTICE: Neither GEMINI_API_KEY nor OPENAI_API_KEY was found in environment.")
        print("      Running in offline simulation mode (MockProvider).")
        print("      To connect to real APIs, set GEMINI_API_KEY or OPENAI_API_KEY in .env.")

    # 5. Execute Extraction
    start_time = time.time()
    try:
        provider = get_provider(
            provider_name=resolved_provider,
            api_key=api_key,
            model_name=model_name,
        )
        print(f"  • Model:           {provider.model_name}")
        print("\n[+] Calling LLM and enforcing Pydantic validation...")

        validated_result = provider.extract(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            target_schema=target_schema,
        )
        duration = time.time() - start_time

        print(f"[✓] Successfully extracted and validated {target_schema.__name__} in {duration:.2f}s!")

        # 6. Pretty Print Key Highlights
        print("-" * 70)
        if doc_type == "invoice":
            inv: Invoice = validated_result
            print(f"  Invoice #:       {inv.invoice_number}")
            print(f"  Date:            {inv.invoice_date}")
            print(f"  Currency:        {inv.currency}")
            print(f"  Vendor:          {inv.vendor.name} ({inv.vendor.email or 'N/A'})")
            print(f"  Customer:        {inv.customer.name}")
            print(f"  Line Items ({len(inv.line_items)}):")
            for item in inv.line_items:
                print(f"    - [{item.quantity:g}x] {item.description:<45} | ${item.total_price:,.2f}")
            print(f"  Subtotal:        ${inv.subtotal:,.2f}")
            print(f"  Discount:       -${inv.discount_total:,.2f}")
            print(f"  Tax Total:       ${inv.tax_total:,.2f}")
            print(f"  Grand Total:     ${inv.grand_total:,.2f}")
            if inv.payment_details:
                print(f"  Payment Terms:   {inv.payment_details.payment_terms or 'N/A'}")
                print(f"  Payment Due:     {inv.payment_details.due_date or 'N/A'}")
        else:
            res: Resume = validated_result
            print(f"  Candidate:       {res.contact_info.full_name}")
            print(f"  Email:           {res.contact_info.email or 'N/A'}")
            print(f"  Phone:           {res.contact_info.phone or 'N/A'}")
            print(f"  Location:        {res.contact_info.location or 'N/A'}")
            print(f"  Summary:         {res.professional_summary[:80] + '...' if res.professional_summary else 'N/A'}")
            print(f"  Work History ({len(res.work_experience)}):")
            for exp in res.work_experience:
                print(f"    - {exp.job_title} at {exp.company} ({exp.start_date} – {exp.end_date})")
            print(f"  Education ({len(res.education)}):")
            for edu in res.education:
                print(f"    - {edu.degree} from {edu.institution} ({edu.graduation_year or 'N/A'})")
            print(f"  Skill Categories ({len(res.skill_categories)}):")
            for cat in res.skill_categories:
                print(f"    - {cat.category_name}: {', '.join(cat.skills[:5])}{'...' if len(cat.skills) > 5 else ''}")
        print("-" * 70)

        # 7. Output JSON
        formatted_json = validated_result.model_dump_json(indent=2)
        if output_path:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(formatted_json)
            print(f"[✓] Full validated JSON saved to: {out_file.resolve()}")
        else:
            print("\nValidated JSON Output:")
            print(formatted_json)

    except Exception as e:
        print(f"\n[-] Extraction/Validation Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="LLM-Powered Document Extractor with Parameterized Prompts and Pydantic Schema Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze default complex invoice using auto-detected provider:
  python main.py -t invoice

  # Analyze a resume file using Google Gemini:
  python main.py -t resume -f path/to/resume.txt -p gemini --api-key YOUR_KEY

  # Analyze an invoice using OpenAI GPT-4o-mini and save JSON:
  python main.py -t invoice -f invoice.txt -p openai -o output/invoice.json

  # Run the full unit test suite:
  python main.py --test

  # Preview the parameterized prompt with few-shot examples:
  python main.py -t invoice --show-prompt
        """,
    )

    parser.add_argument(
        "-t",
        "--document-type",
        choices=["invoice", "resume"],
        default="invoice",
        help="Type of document to parse: 'invoice' or 'resume' (default: invoice)",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Path to the document text file (defaults to complex realistic sample if omitted)",
    )
    parser.add_argument(
        "-p",
        "--provider",
        choices=["auto", "gemini", "openai", "mock"],
        default="auto",
        help="LLM provider: 'gemini', 'openai', 'mock', or 'auto' (default: auto)",
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Model name (e.g., gemini-2.5-flash or gpt-4o-mini)",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        help="API key override (or use GEMINI_API_KEY / OPENAI_API_KEY environment variables)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to output JSON file destination",
    )
    parser.add_argument(
        "--no-few-shot",
        action="store_true",
        help="Disable few-shot demonstration examples in prompt",
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Display the rendered parameterized prompt template and exit",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-test verification suite",
    )

    args = parser.parse_args()

    if args.test:
        from tests.test_schemas import (
            test_invoice_schema_valid,
            test_invoice_financial_mismatch_raises_error,
            test_resume_schema_valid,
            test_prompt_builder,
            test_clean_json_text,
            test_mock_provider_invoice_extraction,
            test_mock_provider_resume_extraction,
        )
        print("Running comprehensive test suite...")
        test_invoice_schema_valid()
        test_invoice_financial_mismatch_raises_error()
        test_resume_schema_valid()
        test_prompt_builder()
        test_clean_json_text()
        test_mock_provider_invoice_extraction()
        test_mock_provider_resume_extraction()
        print("\nAll tests passed successfully!")
        return

    run_pipeline(
        document_type=args.document_type,
        file_path=args.file,
        provider_name=args.provider,
        model_name=args.model,
        api_key=args.api_key,
        use_few_shot=not args.no_few_shot,
        output_path=args.output,
        show_prompt=args.show_prompt,
    )


if __name__ == "__main__":
    main()
