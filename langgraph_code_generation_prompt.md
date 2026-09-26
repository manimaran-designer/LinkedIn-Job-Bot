# LangGraph + LangChain Code Generation Prompt

You are an expert Python developer specializing in LangGraph and LangChain. 
Generate a production-ready LinkedIn Job Bot Agent using LangGraph workflow framework.

## PROJECT OVERVIEW
Build a LinkedIn Job Bot Agent that:
- Authenticates with LinkedIn (Phase 0)
- Loads resume and configuration files (Phase 1)
- Scrapes LinkedIn jobs with filters (Phase 2)
- Matches jobs against resume skills (Phase 3)
- Conditionally processes jobs (research, mock questions, resume customization) (Phase 3)
- Applies to jobs automatically based on config (Phase 3)
- Tracks applications and generates output (Phase 4-5)

## TECHNOLOGY STACK
- **Framework**: LangGraph (State Machine & Workflow Orchestration)
- **LLM Integration**: LangChain (LLMs for skill matching, company research, mock questions)
- **Web Automation**: Selenium/Playwright (for LinkedIn login & Easy Apply clicks)
- **Data Processing**: Pandas (for resume parsing, tracking, CSV export)
- **File Handling**: PyPDF2/python-docx (for PDF/DOC resume parsing)
- **Config**: YAML/JSON (for user configuration)
- **Logging**: Python logging module

## PROJECT STRUCTURE
```
LinkedIn_Job_Bot/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py               # State schema definitions
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── auth_nodes.py       # Phase 0: LinkedIn login, 2FA, retry logic
│   │   │   ├── load_nodes.py       # Phase 1: Resume, config, blacklist loader
│   │   │   ├── scraper_nodes.py    # Phase 2: LinkedIn job scraper
│   │   │   ├── filter_nodes.py     # Phase 3: Job filtering, skill matching
│   │   │   ├── processor_nodes.py  # Phase 3: Research, mock questions, resume
│   │   │   ├── apply_nodes.py      # Phase 3: Auto-apply logic
│   │   │   ├── tracking_nodes.py   # Phase 3&4: Update tracking, aggregate
│   │   │   └── output_nodes.py     # Phase 5: CSV export, console summary
│   │   ├── edges.py                # Edge routers and conditions
│   │   └── graph_builder.py        # LangGraph workflow construction
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── resume_parser.py        # PDF/DOC parsing
│   │   ├── config_parser.py        # Config file loading
│   │   ├── linkedin_client.py      # LinkedIn scraper & automation
│   │   ├── skill_matcher.py        # LLM-based skill matching
│   │   └── logger.py               # Logging setup
│   └── models/
│       ├── __init__.py
│       ├── schemas.py              # Pydantic models for all data structures
│       └── enums.py                # Enums for states, error types
├── config/
│   └── config.yaml                 # User configuration template
├── data/
│   ├── resume.pdf                  # User's resume file
│   ├── applied_jobs.xlsx           # Tracking spreadsheet
│   └── blacklist.txt               # Blacklist companies
├── output/
│   └── matched_jobs.csv            # Final results
├── tests/
│   ├── __init__.py
│   ├── test_nodes.py
│   ├── test_edges.py
│   └── test_integration.py
├── requirements.txt
├── .env.example                    # Environment variables template
└── README.md
```

## STATE SCHEMA (Pydantic Models)

```python
# Define complete state using TypedDict or Pydantic

from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime

# Phase 0: Authentication State
@dataclass
class LoginState:
    email: str
    password: str
    is_authenticated: bool = False
    session_token: Optional[str] = None
    cookies: Dict = field(default_factory=dict)
    csrf_token: Optional[str] = None
    retry_count: int = 0
    last_error: Optional[str] = None
    error_type: Optional[Literal['InvalidCreds', '2FA', 'Captcha', 'RateLimit', 'SessionTimeout', 'NetworkError']] = None
    require_2fa: bool = False
    login_timestamp: Optional[datetime] = None

# Phase 1: Resume & Config State
@dataclass
class ResumeData:
    skills: List[str]
    roles: List[str]
    experience_level: str
    education: str
    full_text: str
    location: str
    years_experience: int

@dataclass
class ConfigData:
    interested_roles: List[str]
    need_company_research: bool
    prepare_mock_questions: bool
    auto_apply: bool
    modify_resume: bool
    skill_threshold: int = 70  # percentage
    search_keywords: List[str]
    location_filter: str
    salary_min: Optional[int] = None
    blacklist_companies: List[str] = field(default_factory=list)

@dataclass
class TrackingData:
    applied_companies: List[str]
    applied_jobs: Dict[str, datetime]  # job_id -> application_date

# Phase 2: Job Scraping State
@dataclass
class Job:
    job_id: str
    title: str
    company: str
    link: str
    requirements: List[str]
    description: str
    salary_range: Optional[str] = None
    job_type: str = "Full-time"
    location: str = "Remote"

@dataclass
class ScrapingState:
    scraped_jobs: List[Job] = field(default_factory=list)
    total_jobs_scraped: int = 0
    scraping_error: Optional[str] = None

# Phase 3: Job Processing State
@dataclass
class ProcessedJob:
    job: Job
    match_score: float  # 0-100
    is_match: bool
    skill_gaps: List[str]
    company_info: Optional[Dict] = None
    mock_questions: Optional[List[str]] = None
    customized_resume: Optional[str] = None
    application_status: Literal['Applied', 'Skipped', 'Queued', 'Failed'] = 'Skipped'
    error_message: Optional[str] = None

@dataclass
class ProcessingState:
    current_job_index: int = 0
    processed_jobs: List[ProcessedJob] = field(default_factory=list)
    matched_jobs: List[ProcessedJob] = field(default_factory=list)
    applied_jobs: List[ProcessedJob] = field(default_factory=list)
    skipped_jobs: List[ProcessedJob] = field(default_factory=list)

# Phase 4-5: Results State
@dataclass
class ResultsState:
    total_scraped: int = 0
    total_matched: int = 0
    total_applied: int = 0
    total_skipped: int = 0
    success_rate: float = 0.0
    processing_time_seconds: float = 0.0
    final_results: List[ProcessedJob] = field(default_factory=list)

# Master State (Combined for LangGraph)
@dataclass
class LinkedInJobBotState:
    # Phase 0
    login_state: LoginState
    
    # Phase 1
    resume_data: Optional[ResumeData] = None
    config_data: Optional[ConfigData] = None
    tracking_data: Optional[TrackingData] = None
    
    # Phase 2
    scraping_state: ScrapingState = field(default_factory=ScrapingState)
    
    # Phase 3
    processing_state: ProcessingState = field(default_factory=ProcessingState)
    
    # Phase 4-5
    results_state: ResultsState = field(default_factory=ResultsState)
    
    # Global control
    current_phase: Literal['INIT', 'AUTH', 'LOAD', 'SCRAPE', 'PROCESS', 'AGGREGATE', 'OUTPUT'] = 'INIT'
    workflow_error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
```

## NODE DEFINITIONS

### **Phase 0: Authentication Nodes**

```python
# auth_nodes.py

async def linkedin_login_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Attempt LinkedIn login with email/password.
    
    Actions:
    1. Extract credentials from state
    2. POST request to LinkedIn login endpoint
    3. Check response status
    4. Handle different response types (success, 2FA, captcha, rate limit, errors)
    5. Store session cookies/token if successful
    6. Update login_state with result
    
    Returns: Updated state with login attempt result
    """
    pass

async def handle_2fa_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Handle 2FA code verification.
    
    Actions:
    1. Prompt user for 2FA code (with 5-minute timeout)
    2. Validate 6-digit format
    3. POST 2FA verification request
    4. Update session if successful
    5. Handle 2FA failures
    
    Returns: Updated state with 2FA result
    """
    pass

async def handle_captcha_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Handle captcha challenge.
    
    Actions:
    1. Notify user of captcha requirement
    2. Wait for manual captcha solve (5-minute timeout)
    3. Continue login process
    
    Returns: Updated state ready for retry
    """
    pass

async def retry_login_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Retry login with exponential backoff.
    
    Actions:
    1. Check retry_count < max_retries
    2. Calculate backoff time based on error_type
    3. Sleep for backoff duration
    4. Increment retry_count
    5. Return to login_node or fail
    
    Returns: Updated state with incremented retry count
    """
    pass

async def validate_session_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Validate that login session is working.
    
    Actions:
    1. Make test request to LinkedIn profile page
    2. Verify cookies/tokens are valid
    3. Check for redirect loops
    4. Confirm authentication status
    
    Returns: Updated state with session validity
    """
    pass

async def login_failure_handler(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Handle login failure after all retries exhausted.
    
    Actions:
    1. Log detailed failure information
    2. Send alert notification (email/Slack optional)
    3. Create error report
    4. Set is_authenticated = False
    5. Set current_phase = 'FAILED'
    
    Returns: Updated state indicating failure
    """
    pass
```

### **Phase 1: Data Loading Nodes**

```python
# load_nodes.py

async def load_resume_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Load and parse resume file (PDF or DOC).
    
    Actions:
    1. Read resume file from {resume_path}
    2. Extract text using PyPDF2 (PDF) or python-docx (DOC)
    3. Parse skills, roles, experience using regex/NLP
    4. Extract education, location, years_experience
    5. Store in resume_data
    
    Returns: Updated state with parsed resume
    """
    pass

async def load_config_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Load and parse configuration file.
    
    Actions:
    1. Read config.yaml
    2. Parse: interested_roles, need_company_research, prepare_mock_questions, 
             auto_apply, modify_resume, skill_threshold
    3. Parse: search_keywords, location_filter, salary_min, blacklist_companies
    4. Validate all required fields
    5. Store in config_data
    
    Returns: Updated state with parsed config
    """
    pass

async def load_blacklist_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Load blacklist and tracking data.
    
    Actions:
    1. Read applied_jobs.xlsx (if exists)
    2. Extract applied_companies list
    3. Extract applied_jobs dictionary {job_id: date}
    4. Store in tracking_data
    5. Create if doesn't exist
    
    Returns: Updated state with tracking data
    """
    pass
```

### **Phase 2: Job Scraping Nodes**

```python
# scraper_nodes.py

async def linkedin_scraper_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Scrape LinkedIn jobs with filters.
    
    Actions:
    1. Build LinkedIn search URL with config parameters:
       - search_keywords
       - location_filter
       - job_type = "Full-time"
       - remote filter = True
       - easy_apply = True
    2. Use Selenium/Playwright to navigate and fetch jobs
    3. Parse DOM or use LinkedIn API if possible
    4. Extract: job_id, title, company, link, requirements, salary_range
    5. Handle pagination
    6. Store in scraping_state.scraped_jobs
    
    Returns: Updated state with scraped jobs
    Timeout: 30 seconds per page, retry on network error
    """
    pass
```

### **Phase 3: Job Processing Nodes**

```python
# filter_nodes.py

async def check_company_blacklist_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Check if company is in blacklist.
    
    Condition: Is company in blacklist?
    YES → Skip job (add to skipped_jobs, mark as 'Skipped')
    NO → Continue to next filter
    
    Returns: Updated state with job marked as skip or continue
    """
    pass

async def check_already_applied_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Check if already applied to this job.
    
    Condition: Is job_id in tracking_data.applied_jobs?
    YES → Skip job
    NO → Continue to skill matching
    
    Returns: Updated state with job marked as skip or continue
    """
    pass

async def skill_matcher_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Match resume skills against job requirements using LLM.
    
    Actions:
    1. Extract job requirements from current job
    2. Extract resume skills from resume_data
    3. Use LangChain + LLM (GPT-4) to:
       - Compare skills semantically
       - Calculate match_percentage (0-100)
       - Identify skill_gaps (what resume is missing)
    4. Create ProcessedJob object with match_score
    5. Threshold check: match_score >= skill_threshold?
       - YES: Add to matched_jobs → Continue processing
       - NO: Add to skipped_jobs → Skip to next job
    
    LLM Prompt:
    "Compare the following resume skills with job requirements and provide:
    1. Match percentage (0-100)
    2. List of missing skills
    
    Resume Skills: {resume.skills}
    Job Requirements: {job.requirements}
    
    Response Format: JSON {match_score: int, skill_gaps: [str]}"
    
    Returns: Updated state with ProcessedJob
    """
    pass

# processor_nodes.py

async def research_company_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Research company information using LLM.
    
    Condition: config_data.need_company_research == True?
    YES: Execute research
    NO: Skip to next processor
    
    Actions:
    1. Extract company name from current job
    2. Use LangChain to search/retrieve company info:
       - Company size
       - Industry
       - Culture/Reviews
       - Recent news
       - Engineering tech stack
    3. Store in ProcessedJob.company_info as Dict
    
    Returns: Updated ProcessedJob with company_info
    """
    pass

async def mock_questions_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Generate mock interview questions using LLM.
    
    Condition: config_data.prepare_mock_questions == True?
    YES: Generate questions
    NO: Skip to next processor
    
    Actions:
    1. Extract job title, company, requirements from current job
    2. Use LangChain + LLM to generate:
       - 3-5 role-specific behavioral questions
       - 3-5 technical questions based on required skills
       - 2-3 company-specific questions
    3. Store in ProcessedJob.mock_questions as List[str]
    
    LLM Prompt:
    "Generate mock interview questions for a {job.title} position at {company}.
    Focus on: {skill_gaps if exists, else required_skills}
    
    Provide 5 technical questions and 5 behavioral questions in JSON format."
    
    Returns: Updated ProcessedJob with mock_questions
    """
    pass

async def resume_customization_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Customize resume for specific job using LLM.
    
    Condition: config_data.modify_resume == True?
    YES: Customize
    NO: Skip to apply node
    
    Actions:
    1. Extract original resume text
    2. Use LangChain + LLM to:
       - Highlight relevant experience
       - Add job-specific keywords
       - Reorder bullet points by relevance
       - Adjust language/tone to match job description
    3. Store in ProcessedJob.customized_resume as string
    4. Note: Do NOT apply to actual LinkedIn resume yet
    
    LLM Prompt:
    "Customize this resume for the {job.title} position at {company}.
    Add keywords from job description and highlight relevant experience.
    
    Resume: {resume.full_text}
    
    Job Description: {job.description}"
    
    Returns: Updated ProcessedJob with customized_resume
    """
    pass

# apply_nodes.py

async def auto_apply_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Automatically apply to job using Easy Apply.
    
    Condition: config_data.auto_apply == True AND all ProcessedJob conditions passed?
    YES: Apply using Selenium/Playwright
    NO: Add to queued_jobs for manual review
    
    Actions:
    1. If auto_apply == False:
       - Mark application_status = 'Queued'
       - Add to processed_jobs (not applied yet)
       - Return to main loop
    2. If auto_apply == True:
       - Use Selenium/Playwright to:
         a. Navigate to job link
         b. Click "Easy Apply" button
         c. Fill form if needed
         d. Submit application
         e. Wait for confirmation
       - Capture application_id or timestamp
       - Handle captcha if appears (user intervention)
    3. Update ProcessedJob:
       - application_status = 'Applied'
       - Applied timestamp
    4. Handle exceptions:
       - Job no longer available → Skip
       - Easy Apply button missing → Skip
       - Network error → Log and continue
    
    Returns: Updated ProcessedJob with application status
    """
    pass
```

### **Phase 4: Tracking & Aggregation Nodes**

```python
# tracking_nodes.py

async def update_tracking_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Update tracking Excel with application results.
    
    Actions:
    1. For each processed job:
       - Add row to tracking Excel (applied_jobs.xlsx)
       - Columns: JobID, Title, Company, Link, MatchScore, 
                  ApplicationStatus, ApplicationDate, Notes
    2. Update blacklist if applied
    3. Save Excel file
    
    Returns: Updated state with current_phase = 'AGGREGATE'
    """
    pass

async def aggregate_results_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Aggregate workflow statistics.
    
    Actions:
    1. Count:
       - total_scraped = len(scraping_state.scraped_jobs)
       - total_matched = len(matched_jobs with match_score >= threshold)
       - total_applied = len(jobs with application_status == 'Applied')
       - total_skipped = total_scraped - total_matched
    2. Calculate:
       - success_rate = (total_applied / total_matched) * 100
       - processing_time = datetime.now() - start_time
    3. Store in results_state
    4. Compile final_results list
    
    Returns: Updated state with aggregated results
    """
    pass
```

### **Phase 5: Output Nodes**

```python
# output_nodes.py

async def export_csv_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Export matched jobs to CSV.
    
    Actions:
    1. Create DataFrame from final_results (ProcessedJob list)
    2. Columns: JobID, Title, Company, Link, MatchScore, 
               ApplicationStatus, SkillGaps, AppliedDate
    3. Sort by MatchScore descending
    4. Save to output/matched_jobs.csv
    
    Returns: Updated state
    """
    pass

async def console_summary_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Print summary to console.
    
    Actions:
    Print:
    ```
    ════════════════════════════════════════════════════════
    LinkedIn Job Bot - Execution Summary
    ════════════════════════════════════════════════════════
    Jobs Scraped:     {total_scraped}
    Jobs Matched:     {total_matched} ({matched_percentage}%)
    Jobs Applied:     {total_applied} ({applied_percentage}%)
    Jobs Skipped:     {total_skipped}
    Success Rate:     {success_rate}%
    Processing Time:  {processing_time} seconds
    
    Top Matched Jobs:
    {top_5_jobs with match scores}
    
    Output File: output/matched_jobs.csv
    Tracking File: data/applied_jobs.xlsx
    
    Last Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ════════════════════════════════════════════════════════
    ```
    
    Returns: Updated state
    """
    pass

async def return_results_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """
    Return results object to caller.
    
    Actions:
    1. Compile final result object:
       {
           success: True,
           matched_jobs: [ProcessedJob],
           stats: {total_scraped, total_matched, total_applied, 
                   success_rate, processing_time},
           errors: [error_messages],
           files: {csv_path, tracking_path}
       }
    2. Set current_phase = 'OUTPUT'
    3. Return as output
    
    Returns: Final state ready for exit
    """
    pass
```

## EDGE ROUTERS & CONDITIONS

```python
# edges.py

def auth_router(state: LinkedInJobBotState) -> str:
    """
    Route based on login response.
    
    Returns:
    - 'handle_2fa' if error_type == '2FA'
    - 'handle_captcha' if error_type == 'Captcha'
    - 'retry_login' if error_type in [RateLimit, SessionTimeout, NetworkError]
    - 'validate_session' if is_authenticated == True
    - 'login_failure' if retry_count >= max_retries
    """
    pass

def filter_router(state: LinkedInJobBotState) -> str:
    """
    Route job processing based on filters.
    
    If current job:
    - In blacklist: 'skip_job'
    - Already applied: 'skip_job'
    - Skill match < threshold: 'skip_job'
    - Skill match >= threshold: 'process_job'
    """
    pass

def processor_router(state: LinkedInJobBotState) -> str:
    """
    Route to processors based on config flags.
    
    If need_company_research: 'research_company'
    Else if prepare_mock_questions: 'mock_questions'
    Else if modify_resume: 'customize_resume'
    Else: 'apply_job'
    """
    pass

def job_loop_router(state: LinkedInJobBotState) -> str:
    """
    Route job processing loop.
    
    If current_job_index < len(scraped_jobs):
        'process_next_job'
    Else:
        'aggregate_results'
    """
    pass
```

## LANGGRAPH CONSTRUCTION

```python
# graph_builder.py

from langgraph.graph import StateGraph, START, END

def build_job_bot_graph() -> StateGraph:
    """
    Build LangGraph workflow.
    
    Structure:
    START
    ├─ Load Credentials
    ├─ LinkedIn Login (Phase 0)
    │  ├─ Login Attempt
    │  ├─ 2FA Handler (conditional)
    │  ├─ Captcha Handler (conditional)
    │  ├─ Retry Logic (conditional)
    │  └─ Validate Session
    │
    ├─ Load Resume & Config (Phase 1)
    │  ├─ Load Resume
    │  ├─ Load Config
    │  └─ Load Blacklist
    │
    ├─ Scrape Jobs (Phase 2)
    │
    ├─ Process Jobs Loop (Phase 3)
    │  ├─ Check Blacklist
    │  ├─ Check Already Applied
    │  ├─ Skill Matching
    │  ├─ Company Research (conditional)
    │  ├─ Mock Questions (conditional)
    │  ├─ Resume Customization (conditional)
    │  ├─ Auto Apply (conditional)
    │  └─ Update Tracking
    │
    ├─ Aggregate Results (Phase 4)
    │
    ├─ Generate Output (Phase 5)
    │  ├─ Export CSV
    │  ├─ Console Summary
    │  └─ Return Results
    │
    └─ END
    """
    
    graph = StateGraph(LinkedInJobBotState)
    
    # Add all nodes
    graph.add_node("login_attempt", linkedin_login_node)
    graph.add_node("handle_2fa", handle_2fa_node)
    graph.add_node("handle_captcha", handle_captcha_node)
    graph.add_node("retry_login", retry_login_node)
    graph.add_node("validate_session", validate_session_node)
    graph.add_node("login_failure", login_failure_handler)
    # ... add all other nodes
    
    # Add edges
    graph.add_edge(START, "login_attempt")
    graph.add_conditional_edges(
        "login_attempt",
        auth_router,
        {
            'handle_2fa': 'handle_2fa',
            'handle_captcha': 'handle_captcha',
            'retry_login': 'retry_login',
            'validate_session': 'validate_session',
            'login_failure': 'login_failure'
        }
    )
    
    # ... add all other conditional edges
    
    graph.add_edge("validate_session", "load_resume")
    graph.add_edge("load_resume", "load_config")
    graph.add_edge("load_config", "load_blacklist")
    graph.add_edge("load_blacklist", "scrape_jobs")
    graph.add_edge("scrape_jobs", "process_jobs_loop")
    
    graph.add_conditional_edges(
        "filter_current_job",
        filter_router,
        {
            'skip_job': 'skip_job',
            'process_job': 'skill_matching'
        }
    )
    
    # ... continue with all edges
    
    graph.add_edge("aggregate_results", "export_csv")
    graph.add_edge("export_csv", "console_summary")
    graph.add_edge("console_summary", "return_results")
    graph.add_edge("return_results", END)
    graph.add_edge("login_failure", END)  # Failure exit
    
    return graph.compile()
```

## UTILITIES & HELPERS

```python
# utils/skill_matcher.py
async def llm_skill_matcher(resume_skills, job_requirements, llm_client):
    """Use LLM to match skills semantically."""
    pass

# utils/linkedin_client.py
class LinkedInClient:
    def __init__(self, session_token, cookies):
        """Initialize with auth credentials."""
        pass
    
    async def login(self, email, password):
        """Handle LinkedIn login via Selenium."""
        pass
    
    async def scrape_jobs(self, keywords, filters):
        """Scrape jobs from LinkedIn."""
        pass
    
    async def easy_apply(self, job_link):
        """Click Easy Apply and submit."""
        pass

# utils/resume_parser.py
async def parse_resume(file_path):
    """Extract text from PDF/DOC resume."""
    pass

async def extract_resume_data(raw_text):
    """Parse resume text into structured data."""
    pass
```

## ERROR HANDLING & LOGGING

```python
# Setup logging for all phases
import logging

logger = logging.getLogger('linkedinjobbot')

# Log retry attempts, API errors, parsing failures
# Log timestamps for performance tracking
# Create detailed error reports
```

## REQUIREMENTS

Create a requirements.txt with:
```
langgraph>=0.1.0
langchain>=0.1.0
langchain-openai>=0.1.0
selenium>=4.0.0
playwright>=1.40.0
pandas>=2.0.0
pyyaml>=6.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
PyPDF2>=3.0.0
python-docx>=0.8.11
openpyxl>=3.1.0
aiohttp>=3.9.0
openai>=1.0.0
pydantic-settings>=2.0.0
```

## EXECUTION ENTRY POINT

```python
# main.py

import asyncio
from dotenv import load_dotenv
from graph.graph_builder import build_job_bot_graph
from models.schemas import LinkedInJobBotState, LoginState, ConfigData, ResumeData, TrackingData
from datetime import datetime

async def main():
    load_dotenv()
    
    # Initialize state with user credentials
    initial_state = LinkedInJobBotState(
        login_state=LoginState(
            email=os.getenv('LINKEDIN_EMAIL'),
            password=os.getenv('LINKEDIN_PASSWORD'),
            require_2fa=os.getenv('REQUIRE_2FA', True)
        ),
        current_phase='INIT',
        start_time=datetime.now()
    )
    
    # Build and compile graph
    graph = build_job_bot_graph()
    
    # Execute workflow
    result = await graph.ainvoke(initial_state)
    
    # Handle completion
    if result['current_phase'] == 'OUTPUT':
        print("✅ Workflow completed successfully!")
    else:
        print("❌ Workflow failed!")
        print(result.get('workflow_error'))

if __name__ == '__main__':
    asyncio.run(main())
```

## KEY REQUIREMENTS FOR CODE GENERATION

1. ✅ Use LangGraph StateGraph for workflow orchestration
2. ✅ Implement all 6 phases (0: Auth, 1: Load, 2: Scrape, 3: Process, 4: Aggregate, 5: Output)
3. ✅ Use async/await throughout for concurrent operations
4. ✅ Implement conditional routing with state-based decision logic
5. ✅ Error handling with retries (exponential backoff for rate limits)
6. ✅ LLM integration for skill matching, company research, mock questions
7. ✅ Selenium/Playwright for LinkedIn automation
8. ✅ Comprehensive logging for debugging
9. ✅ Pydantic models for type safety
10. ✅ CSV export and console summary
11. ✅ Excel tracking spreadsheet management
12. ✅ Configuration file support (YAML)
13. ✅ 2FA handling with user input
14. ✅ Blacklist and already-applied job filtering
15. ✅ Auto-apply toggle with manual queue option
