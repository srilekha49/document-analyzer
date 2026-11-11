"""
Mock LLM Provider for offline demonstration, testing, and CI/CD without API keys.
"""

import json
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from .base import LLMProvider

T = TypeVar("T", bound=BaseModel)


class MockProvider(LLMProvider):
    """
    Simulates LLM extraction output for testing and demonstration purposes.
    Returns valid schema-compliant data based on document contents or type.
    """

    def __init__(self, api_key: Optional[str] = "mock_key", model_name: str = "mock-model"):
        super().__init__(api_key=api_key or "mock_key", model_name=model_name)

    def generate_raw(self, system_prompt: str, user_prompt: str, target_schema: Type[T]) -> str:
        schema_name = target_schema.__name__

        if schema_name == "Invoice":
            sample_invoice = {
                "invoice_number": "INV-2024-9982",
                "invoice_date": "2024-04-10",
                "purchase_order_number": "PO-GLOBAL-441",
                "currency": "USD",
                "vendor": {
                    "name": "Global Data Solutions Inc.",
                    "address": "400 Enterprise Way, Suite 300, Austin, TX 78701",
                    "tax_id": "EIN-74-3928104",
                    "email": "invoicing@globaldatasolutions.io",
                    "phone": "+1 (512) 555-0188",
                    "website": "https://globaldatasolutions.io"
                },
                "customer": {
                    "name": "Meridian Health Logistics Corp",
                    "billing_address": "1200 Healthcare Drive, Bldg B, Chicago, IL 60601",
                    "shipping_address": "1200 Healthcare Drive, Receiving Dock 3, Chicago, IL 60601",
                    "contact_name": "Marcus Vance",
                    "contact_email": "m.vance@meridianhealth.com",
                    "contact_phone": "+1 (312) 555-8921"
                },
                "line_items": [
                    {
                        "item_code": "SAAS-ENT-01",
                        "description": "Enterprise Analytics Platform License (Annual Seat x 20)",
                        "quantity": 20.0,
                        "unit_price": 450.0,
                        "discount_amount": 0.0,
                        "tax_rate_percent": 0.0,
                        "total_price": 9000.0
                    },
                    {
                        "item_code": "CONS-IMP-02",
                        "description": "Custom ETL Integration Consulting & Data Migration (Hours)",
                        "quantity": 35.0,
                        "unit_price": 180.0,
                        "discount_amount": 0.0,
                        "tax_rate_percent": 0.0,
                        "total_price": 6300.0
                    },
                    {
                        "item_code": "SUP-PREM-03",
                        "description": "24/7 Dedicated SLA Support Package",
                        "quantity": 1.0,
                        "unit_price": 1200.0,
                        "discount_amount": 0.0,
                        "tax_rate_percent": 0.0,
                        "total_price": 1200.0
                    }
                ],
                "subtotal": 16500.0,
                "discount_total": 500.0,
                "tax_total": 1320.0,
                "shipping_fee": 0.0,
                "grand_total": 17320.0,
                "payment_details": {
                    "payment_terms": "Net 30",
                    "due_date": "2024-05-10",
                    "bank_name": "Chase Commercial Banking",
                    "account_number": "8821940192",
                    "routing_number": "071000013",
                    "payment_method": "ACH / Fedwire",
                    "payment_status": "Unpaid"
                },
                "notes_or_terms": "Payment due within 30 days of invoice date. Late fees of 1.5% apply after May 10, 2024."
            }
            return json.dumps(sample_invoice, indent=2)

        elif schema_name == "Resume":
            sample_resume = {
                "contact_info": {
                    "full_name": "Samantha K. Reed",
                    "email": "samantha.reed.ai@gmail.com",
                    "phone": "(415) 555-3921",
                    "location": "San Francisco, CA",
                    "linkedin_url": "https://linkedin.com/in/samanthareed-ml",
                    "github_url": "https://github.com/sreed-ai",
                    "portfolio_url": "https://samanthareed.dev"
                },
                "professional_summary": "Lead Machine Learning Engineer with 7+ years of experience building, deploying, and optimizing generative AI pipelines, LLM fine-tuning, and low-latency computer vision systems in production.",
                "education": [
                    {
                        "degree": "Master of Science in Computer Science (AI Specialization)",
                        "institution": "Stanford University",
                        "location": "Stanford, CA",
                        "start_year": "2015",
                        "graduation_year": "2017",
                        "gpa": "3.91/4.00",
                        "honors_and_awards": ["Graduate Research Fellowship", "Best Paper Finalist CVPR Workshop"]
                    },
                    {
                        "degree": "Bachelor of Science in Electrical Engineering & Computer Science",
                        "institution": "UC Berkeley",
                        "location": "Berkeley, CA",
                        "start_year": "2011",
                        "graduation_year": "2015",
                        "gpa": "3.88/4.00",
                        "honors_and_awards": ["Eta Kappa Nu Honor Society", "Summa Cum Laude"]
                    }
                ],
                "work_experience": [
                    {
                        "job_title": "Lead Machine Learning Engineer",
                        "company": "NeuralEdge Technologies",
                        "location": "San Francisco, CA",
                        "start_date": "2021-04",
                        "end_date": "Present",
                        "is_current": True,
                        "responsibilities_and_achievements": [
                            "Spearheaded multi-tenant RAG retrieval platform serving 2M daily queries, cutting hallucination rates by 42% through semantic hybrid reranking.",
                            "Optimized model inference latency from 220ms to 48ms using TensorRT-LLM and vLLM quantization on NVIDIA H100 clusters.",
                            "Directed cross-functional team of 8 ML engineers and data scientists delivering quarterly product releases."
                        ],
                        "technologies_used": ["Python", "PyTorch", "vLLM", "TensorRT", "FastAPI", "Ray", "Triton Inference Server", "AWS"]
                    },
                    {
                        "job_title": "Senior AI Research Engineer",
                        "company": "VisionStream Systems",
                        "location": "Palo Alto, CA",
                        "start_date": "2017-08",
                        "end_date": "2021-03",
                        "is_current": False,
                        "responsibilities_and_achievements": [
                            "Developed deep learning semantic segmentation models for real-time robotic perception achieving 94.6% mIoU at 60 FPS.",
                            "Authored 3 provisional patents on sparse attention mechanisms for high-resolution video streams."
                        ],
                        "technologies_used": ["Python", "C++", "PyTorch", "CUDA", "OpenCV", "Docker", "GCP"]
                    }
                ],
                "skill_categories": [
                    {
                        "category_name": "Programming Languages",
                        "skills": ["Python", "C++", "SQL", "CUDA", "Bash"]
                    },
                    {
                        "category_name": "ML & Deep Learning Frameworks",
                        "skills": ["PyTorch", "Hugging Face", "vLLM", "TensorRT-LLM", "LangChain", "DeepSpeed"]
                    },
                    {
                        "category_name": "Cloud, Infrastructure & MLOps",
                        "skills": ["AWS (SageMaker, EKS)", "GCP (Vertex AI)", "Docker", "Kubernetes", "Ray", "Triton Server", "MLflow"]
                    },
                    {
                        "category_name": "Databases & Vector Stores",
                        "skills": ["Milvus", "Pinecone", "Qdrant", "PostgreSQL (pgvector)", "Redis"]
                    }
                ],
                "projects": [
                    {
                        "project_name": "Open-RAG-Benchmark",
                        "description": "Open-source evaluation harness comparing 12 embedding models and rerankers across financial and legal document QA.",
                        "role": "Creator & Lead Maintainer",
                        "technologies_used": ["Python", "FastAPI", "PostgreSQL", "Streamlit"],
                        "project_url": "https://github.com/sreed-ai/open-rag-benchmark"
                    }
                ],
                "certifications": [
                    {
                        "name": "AWS Certified Machine Learning - Specialty",
                        "issuing_organization": "Amazon Web Services",
                        "issue_date": "2022-05",
                        "expiration_date": "2025-05",
                        "credential_id": "AWS-MLS-882019"
                    }
                ],
                "languages_spoken": ["English (Native)", "Mandarin (Professional Working)"]
            }
            return json.dumps(sample_resume, indent=2)

        return "{}"
