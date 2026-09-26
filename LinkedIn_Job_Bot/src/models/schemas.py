from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from models.enums import ErrorType, ApplicationStatus, Phase

class LoginState(BaseModel):
    email: str
    password: str
    is_authenticated: bool = False
    session_token: Optional[str] = None
    cookies: Dict = Field(default_factory=dict)
    csrf_token: Optional[str] = None
    retry_count: int = 0
    last_error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    require_2fa: bool = False
    login_timestamp: Optional[datetime] = None

class ResumeData(BaseModel):
    skills: List[str]
    roles: List[str]
    experience_level: str
    education: str
    full_text: str
    location: str
    years_experience: int

class ConfigData(BaseModel):
    interested_roles: List[str]
    need_company_research: bool
    prepare_mock_questions: bool
    auto_apply: bool
    modify_resume: bool
    skill_threshold: int = 70
    search_keywords: List[str]
    location_filter: str
    salary_min: Optional[int] = None
    blacklist_companies: List[str] = Field(default_factory=list)

class TrackingData(BaseModel):
    applied_companies: List[str]
    applied_jobs: Dict[str, datetime]

class Job(BaseModel):
    job_id: str
    title: str
    company: str
    link: str
    requirements: List[str]
    description: str
    salary_range: Optional[str] = None
    job_type: str = "Full-time"
    location: str = "Remote"

class ScrapingState(BaseModel):
    scraped_jobs: List[Job] = Field(default_factory=list)
    total_jobs_scraped: int = 0
    scraping_error: Optional[str] = None

class ProcessedJob(BaseModel):
    job: Job
    match_score: float
    is_match: bool
    skill_gaps: List[str]
    company_info: Optional[Dict] = None
    mock_questions: Optional[List[str]] = None
    customized_resume: Optional[str] = None
    application_status: ApplicationStatus = ApplicationStatus.SKIPPED
    error_message: Optional[str] = None

class ProcessingState(BaseModel):
    current_job_index: int = 0
    processed_jobs: List[ProcessedJob] = Field(default_factory=list)
    matched_jobs: List[ProcessedJob] = Field(default_factory=list)
    applied_jobs: List[ProcessedJob] = Field(default_factory=list)
    skipped_jobs: List[ProcessedJob] = Field(default_factory=list)

class ResultsState(BaseModel):
    total_scraped: int = 0
    total_matched: int = 0
    total_applied: int = 0
    total_skipped: int = 0
    success_rate: float = 0.0
    processing_time_seconds: float = 0.0
    final_results: List[ProcessedJob] = Field(default_factory=list)

class LinkedInJobBotState(BaseModel):
    # Phase 0
    login_state: LoginState
    # Phase 1
    resume_data: Optional[ResumeData] = None
    config_data: Optional[ConfigData] = None
    tracking_data: Optional[TrackingData] = None
    # Phase 2
    scraping_state: ScrapingState = Field(default_factory=ScrapingState)
    # Phase 3
    processing_state: ProcessingState = Field(default_factory=ProcessingState)
    # Phase 4-5
    results_state: ResultsState = Field(default_factory=ResultsState)
    # Global control
    current_phase: Phase = Phase.INIT
    workflow_error: Optional[str] = None
    start_time: datetime = Field(default_factory=datetime.now)
