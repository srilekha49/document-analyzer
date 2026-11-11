"""
Pydantic schema definitions and validation rules for Resume/CV Extraction.
"""

from typing import List, Optional
import re
from pydantic import BaseModel, Field, field_validator, model_validator


class ContactInfo(BaseModel):
    full_name: str = Field(description="Full name of the candidate")
    email: Optional[str] = Field(default=None, description="Primary email address")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    location: Optional[str] = Field(default=None, description="Current location (City, State/Country)")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(default=None, description="Personal website or portfolio URL")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        cleaned = v.strip().lower()
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, cleaned):
            # If the LLM extracted something malformed, return cleaned or none
            return cleaned
        return cleaned

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Candidate name cannot be empty")
        return cleaned


class EducationEntry(BaseModel):
    degree: str = Field(description="Degree or qualification (e.g., B.S. in Computer Science)")
    institution: str = Field(description="University, college, or academic institution")
    location: Optional[str] = Field(default=None, description="Institution location (City, State/Country)")
    start_year: Optional[str] = Field(default=None, description="Start year or date")
    graduation_year: Optional[str] = Field(default=None, description="Graduation year, date, or 'Expected 2026'")
    gpa: Optional[str] = Field(default=None, description="Grade point average or grade division")
    honors_and_awards: List[str] = Field(default_factory=list, description="Academic honors, awards, or Dean's list")


class ExperienceEntry(BaseModel):
    job_title: str = Field(description="Job title or designation")
    company: str = Field(description="Employer or company name")
    location: Optional[str] = Field(default=None, description="Work location or 'Remote'")
    start_date: Optional[str] = Field(default=None, description="Start date (e.g., Jun 2021 or 2021-06)")
    end_date: Optional[str] = Field(default=None, description="End date (e.g., Present, Aug 2023, or 2023-08)")
    is_current: bool = Field(default=False, description="True if this is the candidate's active/current position")
    responsibilities_and_achievements: List[str] = Field(
        default_factory=list,
        description="Key accomplishments, quantified impact, and core duties"
    )
    technologies_used: List[str] = Field(
        default_factory=list,
        description="Tools, languages, libraries, and frameworks utilized in this role"
    )


class ProjectEntry(BaseModel):
    project_name: str = Field(description="Title of the project")
    description: str = Field(description="Brief overview of the project and impact")
    role: Optional[str] = Field(default=None, description="Candidate's specific role in the project")
    technologies_used: List[str] = Field(default_factory=list, description="Tech stack used")
    project_url: Optional[str] = Field(default=None, description="Repository or live URL")


class SkillCategory(BaseModel):
    category_name: str = Field(
        description="Category classification, e.g., 'Languages', 'Frameworks & Libraries', 'Cloud & DevOps', 'Databases'"
    )
    skills: List[str] = Field(description="List of specific skill names")


class CertificationEntry(BaseModel):
    name: str = Field(description="Certification or credential title")
    issuing_organization: Optional[str] = Field(default=None, description="Issuing body (e.g. AWS, Google Cloud, Cisco)")
    issue_date: Optional[str] = Field(default=None, description="Date issued")
    expiration_date: Optional[str] = Field(default=None, description="Date expired or valid until")
    credential_id: Optional[str] = Field(default=None, description="Credential ID or verification license number")


class Resume(BaseModel):
    contact_info: ContactInfo = Field(description="Candidate contact information")
    professional_summary: Optional[str] = Field(
        default=None, description="Executive summary, objective, or profile statement"
    )
    education: List[EducationEntry] = Field(default_factory=list, description="Academic background")
    work_experience: List[ExperienceEntry] = Field(default_factory=list, description="Professional employment history")
    skill_categories: List[SkillCategory] = Field(
        default_factory=list, description="Categorized technical and soft skills"
    )
    projects: List[ProjectEntry] = Field(default_factory=list, description="Key software or research projects")
    certifications: List[CertificationEntry] = Field(
        default_factory=list, description="Professional certifications and licenses"
    )
    languages_spoken: List[str] = Field(
        default_factory=list, description="Natural languages spoken and proficiency"
    )

    @model_validator(mode="after")
    def validate_content_presence(self) -> "Resume":
        # A resume must have either work experience, education, or projects
        if not self.work_experience and not self.education and not self.projects:
            raise ValueError("Resume must contain at least one work experience, education entry, or project")
        return self
