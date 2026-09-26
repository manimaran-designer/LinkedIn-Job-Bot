from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from models.schemas import Job
import json
import logging

logger = logging.getLogger('linkedinjobbot.skill_matcher')

class SkillMatcher:
    def __init__(self):
        # Fallback dictionary if LLM fails or API key missing
        pass

    async def llm_skill_matcher(self, resume_skills: List[str], job_requirements: List[str], llm_client: ChatOpenAI) -> Dict:
        """Use LLM to match skills semantically."""
        prompt = PromptTemplate(
            input_variables=["resume_skills", "job_requirements"],
            template="""
            Compare the following resume skills with job requirements and provide:
            1. Match percentage (0-100)
            2. List of missing skills
            
            Resume Skills: {resume_skills}
            Job Requirements: {job_requirements}
            
            Provide the response STRICTLY in valid JSON format:
            {{"match_score": int, "skill_gaps": ["skill1", "skill2"]}}
            """
        )
        try:
            chain = prompt | llm_client
            # In a real app we parse output using output parsers
            response = await chain.ainvoke({
                "resume_skills": ", ".join(resume_skills),
                "job_requirements": ", ".join(job_requirements)
            })
            # Clean possible markdown formatting
            content = response.content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"LLM Matching failed: {e}. Falling back to basic overlap.")
            return self._basic_matcher(resume_skills, job_requirements)
            
    def _basic_matcher(self, resume_skills: List[str], job_requirements: List[str]) -> Dict:
        """Fallback basic matching"""
        reqs = set([r.lower() for r in job_requirements])
        skills = set([s.lower() for s in resume_skills])
        matches = reqs.intersection(skills)
        score = (len(matches) / len(reqs) * 100) if reqs else 100
        gaps = list(reqs - skills)
        return {"match_score": score, "skill_gaps": gaps}

    async def research_company(self, company: str, llm_client: ChatOpenAI) -> Dict:
        """Use LangChain to research company info."""
        prompt = PromptTemplate(
            input_variables=["company"],
            template="""Briefly describe the company {company}. Focus on industry, size, and main product.
            Output as JSON: {{"industry": str, "description": str}}"""
        )
        try:
            chain = prompt | llm_client
            res = await chain.ainvoke({"company": company})
            content = res.content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception:
            return {"industry": "Unknown", "description": f"Info not found for {company}"}

    async def generate_mock_questions(self, job: Job, llm_client: ChatOpenAI, skill_gaps: List[str] = []) -> List[str]:
        prompt = PromptTemplate(
            input_variables=["title", "company", "gaps"],
            template="""Generate 3 mock interview questions for a {title} position at {company}.
            Focus on these missing skills if any: {gaps}.
            Output as valid JSON array of strings: ["q1", "q2", "q3"]"""
        )
        try:
            chain = prompt | llm_client
            res = await chain.ainvoke({
                "title": job.title, "company": job.company, "gaps": ", ".join(skill_gaps)
            })
            content = res.content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        except Exception:
            return [f"Tell me about your experience related to {job.title}?"]

    async def customize_resume(self, resume_text: str, job: Job, llm_client: ChatOpenAI) -> str:
        prompt = PromptTemplate(
            input_variables=["resume_text", "job_title", "company"],
            template="""Customize this resume slightly for the {job_title} position at {company}.
            Return only the customized resume body text.
            Resume: {resume_text}
            """
        )
        try:
            chain = prompt | llm_client
            res = await chain.ainvoke({
                "resume_text": resume_text, "job_title": job.title, "company": job.company
            })
            return res.content.strip()
        except Exception:
            return resume_text
