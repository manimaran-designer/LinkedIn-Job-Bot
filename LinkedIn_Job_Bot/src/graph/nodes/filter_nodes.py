from graph.state import LinkedInJobBotState, ProcessedJob, ApplicationStatus
from utils.logger import get_logger
from utils.skill_matcher import SkillMatcher
from langchain_openai import ChatOpenAI
import os

logger = get_logger('linkedinjobbot.nodes.filter')

def _get_current_job(state: LinkedInJobBotState):
    idx = state.processing_state.current_job_index
    jobs = state.scraping_state.scraped_jobs
    if idx < len(jobs):
        return jobs[idx]
    return None

async def check_company_blacklist_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: check_company_blacklist_node ---")
    job = _get_current_job(state)
    if not job: return state

    blacklist = state.config_data.blacklist_companies if state.config_data else []
    
    if job.company in blacklist:
        logger.warning(f"Skipping {job.company} - Blacklisted")
        pj = ProcessedJob(job=job, match_score=0, is_match=False, skill_gaps=[], application_status=ApplicationStatus.SKIPPED)
        state.processing_state.skipped_jobs.append(pj)
        state.processing_state.processed_jobs.append(pj)
        # Advance index early since we skip
        state.processing_state.current_job_index += 1
        
    return state

async def check_already_applied_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: check_already_applied_node ---")
    job = _get_current_job(state)
    if not job: return state
        
    # Check if we already skipped in the previous node
    if any(pj.job.job_id == job.job_id for pj in state.processing_state.skipped_jobs):
        return state

    applied_dict = state.tracking_data.applied_jobs if state.tracking_data else {}
    
    if job.job_id in applied_dict:
        logger.warning(f"Skipping {job.job_id} - Already applied")
        pj = ProcessedJob(job=job, match_score=0, is_match=False, skill_gaps=[], application_status=ApplicationStatus.SKIPPED)
        state.processing_state.skipped_jobs.append(pj)
        state.processing_state.processed_jobs.append(pj)
        state.processing_state.current_job_index += 1
        
    return state

async def skill_matcher_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: skill_matcher_node ---")
    job = _get_current_job(state)
    if not job: return state
        
    # Skip if processed
    if any(pj.job.job_id == job.job_id for pj in state.processing_state.processed_jobs):
        return state

    matcher = SkillMatcher()
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv('OPENAI_API_KEY', 'dummy')) # default placeholder fallback
    
    resume_skills = state.resume_data.skills if state.resume_data else []
    res = await matcher.llm_skill_matcher(resume_skills, job.requirements, llm)
    
    score = res.get("match_score", 0)
    gaps = res.get("skill_gaps", [])
    threshold = state.config_data.skill_threshold if state.config_data else 70
    
    is_match = score >= threshold
    
    pj = ProcessedJob(
        job=job,
        match_score=score,
        is_match=is_match,
        skill_gaps=gaps
    )
    
    if is_match:
        logger.info(f"Job {job.job_id} MATCHED (Score: {score}%)")
        state.processing_state.matched_jobs.append(pj)
        # Setup temporary holder in processed_jobs so subsequent nodes can mutate it
        state.processing_state.processed_jobs.append(pj)
    else:
        logger.info(f"Job {job.job_id} SKIPPED (Score: {score}% < {threshold}%)")
        pj.application_status = ApplicationStatus.SKIPPED
        state.processing_state.skipped_jobs.append(pj)
        state.processing_state.processed_jobs.append(pj)
        state.processing_state.current_job_index += 1
        
    return state
