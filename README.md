# LLM-Powered Document Analyzer: Invoices & Resumes

A robust, enterprise-grade Python application that connects to **Google Gemini** or **OpenAI** APIs, leverages **parameterized prompt templates** with **few-shot examples**, and enforces **strictly validated JSON outputs** using **Pydantic v2**.

---

## Key Features

1. **Dual Provider Support**:
   - **Google Gemini**: Uses the official `google-genai` SDK with native structured output schema constraints (`response_schema`, `application/json`).
   - **OpenAI**: Uses the modern `openai` client with strict structured outputs (`client.beta.chat.completions.parse`).
   - **Mock/Offline Provider**: Built-in fallback allowing full execution and end-to-end testing without external API credits or network access.

2. **Parameterized Prompt Engineering**:
   - Clean prompt templating separating System Instructions, Pydantic JSON Schema, Extraction Constraints, Few-Shot Demonstrations, and the target Document Text.
   - Few-shot examples tailored specifically for complex, noisy invoices and multi-section resumes.

3. **Strict Pydantic v2 Schema Validation**:
   - **Invoice Schema (`Invoice`)**: Extracts vendor information, customer details, line items (SKU, quantity, unit price, totals), tax rates, discounts, shipping, grand totals, and payment/remittance details. Enforces cross-field financial reconciliation (`subtotal - discount + tax + shipping == grand total`).
   - **Resume Schema (`Resume`)**: Extracts contact info, email validation, LinkedIn/GitHub links, executive summary, categorized skills, chronologically ordered work experience, education, projects, and certifications.

4. **Resilient JSON Parser & Cleaner**:
   - Automatically handles markdown fences (````json ... ````), isolates JSON objects, and reports granular schema errors if validation fails.

---

## Directory Structure

```
document_analyzer/
├── main.py                     # Primary executable CLI script
├── requirements.txt            # Dependency specification
├── .env.example                # Sample environment configuration
├── schemas/
│   ├── __init__.py
│   ├── invoice.py              # Pydantic models & validators for invoices
│   └── resume.py               # Pydantic models & validators for resumes
├── prompts/
│   ├── __init__.py
│   ├── templates.py            # Parameterized prompt builder & system prompts
│   └── few_shot_examples.py    # Few-shot demonstration examples
├── providers/
│   ├── __init__.py             # Provider factory
│   ├── base.py                 # Abstract base class & JSON sanitizers
│   ├── gemini_provider.py      # Google Gemini client implementation
│   ├── openai_provider.py      # OpenAI client implementation
│   └── mock_provider.py        # Offline test provider
├── samples/
│   ├── sample_invoice_complex.txt  # Real-world noisy invoice text
│   └── sample_resume_complex.txt   # Multi-page unstructured resume text
├── tests/
│   ├── __init__.py
│   └── test_schemas.py         # Full unit test suite (7 tests)
└── output/                     # Exported validated JSON files
```

---

## Setup & Installation

### 1. Requirements
- Python 3.10+ (tested on Python 3.13)
- `pydantic>=2.7.0`
- `python-dotenv>=1.0.0`
- `google-genai>=1.0.0`
- `openai>=1.30.0`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. API Keys Configuration
Copy `.env.example` to `.env` and configure your API keys:
```bash
cp .env.example .env
```
In `.env`:
```env
# Gemini API Key: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API Key: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Default provider: gemini, openai, or mock
DEFAULT_LLM_PROVIDER=gemini
```

*(Note: If no API key is configured, the application automatically switches to `MockProvider`, ensuring scripts remain fully executable).*

---

## Usage Guide

### 1. Extract Invoice Data
Extract structured data from the default complex invoice sample:
```bash
python main.py -t invoice
```

Or analyze a custom invoice file and save the validated JSON:
```bash
python main.py -t invoice -f path/to/my_invoice.txt -p gemini -o output/invoice.json
```

### 2. Extract Resume Data
Extract structured candidate details from an unstructured resume:
```bash
python main.py -t resume -f path/to/candidate_cv.txt -p openai -o output/resume.json
```

### 3. Inspect Parameterized Prompt
To inspect how the parameterized prompt builds dynamic schema definitions and few-shot sections:
```bash
python main.py -t invoice --show-prompt
```

### 4. Run Verification Test Suite
Execute the comprehensive test suite verifying schema validation, mathematical reconciliation, prompt building, and mock extraction:
```bash
python main.py --test
# or directly:
python tests/test_schemas.py
```

---

## CLI Options

| Argument | Short | Description | Default |
|---|---|---|---|
| `--document-type` | `-t` | Document schema to target: `invoice` or `resume` | `invoice` |
| `--file` | `-f` | Path to unstructured text document file | Built-in sample |
| `--provider` | `-p` | LLM provider: `auto`, `gemini`, `openai`, or `mock` | `auto` |
| `--model` | `-m` | Model name (e.g. `gemini-2.5-flash`, `gpt-4o-mini`) | Provider default |
| `--api-key` | `-k` | Explicit API key override | Env variable |
| `--output` | `-o` | File path to write the formatted JSON result | Stdout |
| `--no-few-shot` | | Disable few-shot examples in prompt | Enabled |
| `--show-prompt` | | Render and print the prompt without calling API | False |
| `--test` | | Run unit test verification suite | False |

---

## Validation & Error Handling

- **Financial Integrity**: Invoices check that `subtotal - discount_total + tax_total + shipping_fee == grand_total` within tolerance. Discrepancies raise a descriptive `ValidationError`.
- **Field Normalization**: Currencies like `$` are converted to standard `USD`, dates are parsed/validated, and empty/whitespace fields are rejected.
- **Fail-Safe Parsing**: Raw LLM output with Markdown backticks or preambles is isolated and stripped before JSON decoding.
