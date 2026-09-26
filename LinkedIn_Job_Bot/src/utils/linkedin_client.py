from models.schemas import Job
from typing import List, Dict
import logging
import asyncio

logger = logging.getLogger('linkedinjobbot.client')

class LinkedInClient:
    def __init__(self, session_token: str = None, cookies: Dict = None):
        self.session_token = session_token
        self.cookies = cookies or {}

    async def login(self, email: str, password: str) -> Dict:
        """Handle LinkedIn login via Selenium (Mocked)."""
        logger.info(f"Simulating Selenium login for {email}")
        await asyncio.sleep(1) # Network mock
        
        # Mock successful login
        return {
            "is_authenticated": True,
            "session_token": "mocked_session_token",
            "csrf_token": "mocked_csrf_token",
            "cookies": {"li_at": "mocked_session_token"}
        }

    async def scrape_jobs(self, keywords: List[str], filters: Dict) -> List[Job]:
        """Scrape jobs from LinkedIn (Mocked)."""
        logger.info(f"Simulating Selenium job scrape for keywords {keywords}")
        await asyncio.sleep(2)
        
        return [
            Job(
                job_id="li_001",
                title="AI Engineer",
                company="TechCorp Innovations",
                link="https://linkedin.com/jobs/view/1",
                requirements=["Python", "LangChain", "OpenRouter", "Docker"],
                description="We are seeking an AI Engineer to build agentic workflows.",
                location="Remote",
                salary_range="$130k-$160k"
            ),
            Job(
                job_id="li_002",
                title="Frontend Developer",
                company="UnwantedCorp", # Blacklisted based on our config mock
                link="https://linkedin.com/jobs/view/2",
                requirements=["React", "TypeScript", "CSS"],
                description="Frontend dev position.",
                location="Remote",
                salary_range="$100k-$120k"
            ),
            Job(
                job_id="li_003",
                title="Software Engineer",
                company="Startup Inc.",
                link="https://linkedin.com/jobs/view/3",
                requirements=["Python", "SQL", "AWS"],
                description="Backend engineer for scaling our core product.",
                location="Remote",
                salary_range="$110k-$140k"
            )
        ]

    async def easy_apply(self, job_link: str) -> bool:
        """Click Easy Apply and submit (Mocked)."""
        logger.info(f"Simulating Easy Apply click for {job_link}")
        await asyncio.sleep(1)
        return True
