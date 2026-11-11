"""
Few-shot examples for Invoice and Resume structured extraction.
"""

INVOICE_FEW_SHOT_EXAMPLES = [
    {
        "input_text": """
ACME Cloud Solutions Inc.
123 Tech Blvd, Suite 400, San Francisco, CA 94107
Tax ID: US-948271049 | billing@acmecloud.io | +1 (415) 555-0199

INVOICE
Invoice #: INV-2024-8841
Issue Date: 2024-03-15
Due Date: 2024-04-14 (Net 30)
PO Reference: PO-99214

Billed To:
Apex Retail Dynamics LLC
Attn: Sarah Jenkins (Accounts Payable)
850 Market Street, 5th Floor, Seattle, WA 98101
sarah.j@apexretail.com

Description                      Qty    Rate      Amount
--------------------------------------------------------
Cloud Enterprise Cluster (March)   1  $3,500.00  $3,500.00
Dedicated Support Tier (Hours)    12    $150.00  $1,800.00
Data Egress Overage (TB)           4     $45.00    $180.00

Subtotal: $5,480.00
Partner Discount (5%): -$274.00
Sales Tax (8.5% on services): $442.51
Shipping / Delivery: $0.00
Grand Total Due: $5,648.51

Remit Payment To:
Silicon Valley Commercial Bank
Acct: 9948271630 | Routing: 121000358
Payment Status: Unpaid
        """.strip(),
        "expected_output": {
            "invoice_number": "INV-2024-8841",
            "invoice_date": "2024-03-15",
            "purchase_order_number": "PO-99214",
            "currency": "USD",
            "vendor": {
                "name": "ACME Cloud Solutions Inc.",
                "address": "123 Tech Blvd, Suite 400, San Francisco, CA 94107",
                "tax_id": "US-948271049",
                "email": "billing@acmecloud.io",
                "phone": "+1 (415) 555-0199",
                "website": "acmecloud.io"
            },
            "customer": {
                "name": "Apex Retail Dynamics LLC",
                "billing_address": "850 Market Street, 5th Floor, Seattle, WA 98101",
                "shipping_address": None,
                "contact_name": "Sarah Jenkins",
                "contact_email": "sarah.j@apexretail.com",
                "contact_phone": None
            },
            "line_items": [
                {
                    "item_code": None,
                    "description": "Cloud Enterprise Cluster (March)",
                    "quantity": 1.0,
                    "unit_price": 3500.0,
                    "discount_amount": 0.0,
                    "tax_rate_percent": None,
                    "total_price": 3500.0
                },
                {
                    "item_code": None,
                    "description": "Dedicated Support Tier (Hours)",
                    "quantity": 12.0,
                    "unit_price": 150.0,
                    "discount_amount": 0.0,
                    "tax_rate_percent": None,
                    "total_price": 1800.0
                },
                {
                    "item_code": None,
                    "description": "Data Egress Overage (TB)",
                    "quantity": 4.0,
                    "unit_price": 45.0,
                    "discount_amount": 0.0,
                    "tax_rate_percent": None,
                    "total_price": 180.0
                }
            ],
            "subtotal": 5480.0,
            "discount_total": 274.0,
            "tax_total": 442.51,
            "shipping_fee": 0.0,
            "grand_total": 5648.51,
            "payment_details": {
                "payment_terms": "Net 30",
                "due_date": "2024-04-14",
                "bank_name": "Silicon Valley Commercial Bank",
                "account_number": "9948271630",
                "routing_number": "121000358",
                "payment_method": "Wire/ACH",
                "payment_status": "Unpaid"
            },
            "notes_or_terms": None
        }
    }
]


RESUME_FEW_SHOT_EXAMPLES = [
    {
        "input_text": """
ALEXANDER R. CHEN
Austin, TX | (512) 555-7821 | alex.chen.dev@gmail.com
LinkedIn: linkedin.com/in/alexchen-dev | GitHub: github.com/alexc-codes

PROFESSIONAL SUMMARY
Senior Backend Software Engineer with 6+ years of experience designing scalable distributed systems, microservices, and asynchronous data pipelines in Python and Go.

EXPERIENCE
Staff Engineer | CloudScale Systems | Austin, TX
July 2021 – Present
- Architected event-driven streaming ingestion processing 45k events/sec using Kafka, FastAPI, and Redis, lowering p99 latency by 38%.
- Mentored 6 junior/mid engineers and established CI/CD automated test gates that reduced regression incidents by 45%.
- Tech stack: Python, FastAPI, Kafka, Redis, Docker, AWS (EKS, RDS, S3).

Backend Developer | Nexus Financial Tech | Dallas, TX
August 2018 – June 2021
- Built secure RESTful payment processing APIs compliant with PCI-DSS specifications using Django and PostgreSQL.
- Reduced database query times by 60% through indexed views and Redis caching layers.
- Tech stack: Python, Django, PostgreSQL, Celery, Docker.

EDUCATION
University of Texas at Austin
Bachelor of Science in Computer Science | Minor in Mathematics
Graduated: May 2018 | GPA: 3.82/4.00
Honors: Dean's List (6 semesters), ACM Programming Finalist

SKILLS
- Languages: Python, Go, SQL, Bash
- Frameworks & Libraries: FastAPI, Django, Flask, Pydantic, SQLAlchemy, Celery
- Databases & Storage: PostgreSQL, Redis, MongoDB
- Cloud & Infrastructure: AWS, Docker, Kubernetes, Terraform, GitHub Actions

CERTIFICATIONS
- AWS Certified Solutions Architect - Associate (Issued: Jan 2023)
        """.strip(),
        "expected_output": {
            "contact_info": {
                "full_name": "Alexander R. Chen",
                "email": "alex.chen.dev@gmail.com",
                "phone": "(512) 555-7821",
                "location": "Austin, TX",
                "linkedin_url": "https://linkedin.com/in/alexchen-dev",
                "github_url": "https://github.com/alexc-codes",
                "portfolio_url": None
            },
            "professional_summary": "Senior Backend Software Engineer with 6+ years of experience designing scalable distributed systems, microservices, and asynchronous data pipelines in Python and Go.",
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of Texas at Austin",
                    "location": None,
                    "start_year": None,
                    "graduation_year": "2018",
                    "gpa": "3.82/4.00",
                    "honors_and_awards": ["Dean's List (6 semesters)", "ACM Programming Finalist"]
                }
            ],
            "work_experience": [
                {
                    "job_title": "Staff Engineer",
                    "company": "CloudScale Systems",
                    "location": "Austin, TX",
                    "start_date": "2021-07",
                    "end_date": "Present",
                    "is_current": True,
                    "responsibilities_and_achievements": [
                        "Architected event-driven streaming ingestion processing 45k events/sec using Kafka, FastAPI, and Redis, lowering p99 latency by 38%.",
                        "Mentored 6 junior/mid engineers and established CI/CD automated test gates that reduced regression incidents by 45%."
                    ],
                    "technologies_used": ["Python", "FastAPI", "Kafka", "Redis", "Docker", "AWS (EKS, RDS, S3)"]
                },
                {
                    "job_title": "Backend Developer",
                    "company": "Nexus Financial Tech",
                    "location": "Dallas, TX",
                    "start_date": "2018-08",
                    "end_date": "2021-06",
                    "is_current": False,
                    "responsibilities_and_achievements": [
                        "Built secure RESTful payment processing APIs compliant with PCI-DSS specifications using Django and PostgreSQL.",
                        "Reduced database query times by 60% through indexed views and Redis caching layers."
                    ],
                    "technologies_used": ["Python", "Django", "PostgreSQL", "Celery", "Docker"]
                }
            ],
            "skill_categories": [
                {
                    "category_name": "Languages",
                    "skills": ["Python", "Go", "SQL", "Bash"]
                },
                {
                    "category_name": "Frameworks & Libraries",
                    "skills": ["FastAPI", "Django", "Flask", "Pydantic", "SQLAlchemy", "Celery"]
                },
                {
                    "category_name": "Databases & Storage",
                    "skills": ["PostgreSQL", "Redis", "MongoDB"]
                },
                {
                    "category_name": "Cloud & Infrastructure",
                    "skills": ["AWS", "Docker", "Kubernetes", "Terraform", "GitHub Actions"]
                }
            ],
            "projects": [],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect - Associate",
                    "issuing_organization": "Amazon Web Services",
                    "issue_date": "2023-01",
                    "expiration_date": None,
                    "credential_id": None
                }
            ],
            "languages_spoken": []
        }
    }
]
