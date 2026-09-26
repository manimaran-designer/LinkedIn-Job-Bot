from graph.state import LinkedInJobBotState, TrackingData, Phase
from utils.logger import get_logger
from utils.config_parser import parse_config
from utils.resume_parser import parse_resume, extract_resume_data
import os

logger = get_logger('linkedinjobbot.nodes.load')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

async def load_resume_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: load_resume_node ---")
    resume_path = os.path.join(BASE_DIR, 'data', 'resume.txt')
    try:
        raw_text = await parse_resume(resume_path)
        state.resume_data = await extract_resume_data(raw_text)
        logger.info(f"Loaded Resume with skills: {state.resume_data.skills}")
    except Exception as e:
        logger.error(f"Failed to load resume: {e}")
        state.workflow_error = str(e)
    return state

async def load_config_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: load_config_node ---")
    config_path = os.path.join(BASE_DIR, 'config', 'config.yaml')
    try:
        state.config_data = parse_config(config_path)
        logger.info(f"Loaded config: auto_apply={state.config_data.auto_apply}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        state.workflow_error = str(e)
    return state

async def load_blacklist_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: load_blacklist_node ---")
    blacklist_path = os.path.join(BASE_DIR, 'data', 'blacklist.txt')
    companies = []
    
    if os.path.exists(blacklist_path):
        with open(blacklist_path, 'r') as f:
            companies = [line.strip() for line in f if line.strip()]
            
    # Combine with config blacklist
    if state.config_data:
        companies.extend(state.config_data.blacklist_companies)
        state.config_data.blacklist_companies = list(set(companies))
        
    logger.info(f"Combined blacklist contains {len(state.config_data.blacklist_companies)} companies.")
    
    state.tracking_data = TrackingData(
        applied_companies=[],
        applied_jobs={}
    )
    
    state.current_phase = Phase.LOAD
    return state
