from graph.state import LinkedInJobBotState, ProcessedJob
from utils.logger import get_logger
from utils.skill_matcher import SkillMatcher
from langchain_openai import ChatOpenAI
import os

logger = get_logger('linkedinjobbot.nodes.processor')

def _get_current_pj(state: LinkedInJobBotState) -> ProcessedJob:
    idx = state.processing_state.current_job_index
    for pj in state.processing_state.processed_jobs:
        if pj.job == state.scraping_state.scraped_jobs[idx]:
            return pj
    return None

async def research_company_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: research_company_node ---")
    pj = _get_current_pj(state)
    if not pj or not pj.is_match: return state

    if getattr(state.config_data, 'need_company_research', False):
        logger.info(f"Researching company {pj.job.company}")
        matcher = SkillMatcher()
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv('OPENAI_API_KEY', 'dummy'))
        info = await matcher.research_company(pj.job.company, llm)
        pj.company_info = info
        
    return state

async def mock_questions_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: mock_questions_node ---")
    pj = _get_current_pj(state)
    if not pj or not pj.is_match: return state

    if getattr(state.config_data, 'prepare_mock_questions', False):
        logger.info(f"Generating mock questions for {pj.job.title}")
        matcher = SkillMatcher()
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv('OPENAI_API_KEY', 'dummy'))
        qs = await matcher.generate_mock_questions(pj.job, llm, pj.skill_gaps)
        pj.mock_questions = qs
        
    return state

async def resume_customization_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: resume_customization_node ---")
    pj = _get_current_pj(state)
    if not pj or not pj.is_match: return state

    if getattr(state.config_data, 'modify_resume', False) and state.resume_data:
        logger.info(f"Customizing resume for {pj.job.title}")
        matcher = SkillMatcher()
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv('OPENAI_API_KEY', 'dummy'))
        custom = await matcher.customize_resume(state.resume_data.full_text, pj.job, llm)
        pj.customized_resume = custom
        
    return state
