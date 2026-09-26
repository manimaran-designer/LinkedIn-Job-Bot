from graph.state import LinkedInJobBotState, ProcessedJob, ApplicationStatus
from utils.logger import get_logger
from utils.linkedin_client import LinkedInClient

logger = get_logger('linkedinjobbot.nodes.apply')

def _get_current_pj(state: LinkedInJobBotState) -> ProcessedJob:
    idx = state.processing_state.current_job_index
    for pj in state.processing_state.processed_jobs:
        if pj.job == state.scraping_state.scraped_jobs[idx]:
            return pj
    return None

async def auto_apply_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: auto_apply_node ---")
    pj = _get_current_pj(state)
    if not pj or not pj.is_match: 
        return state

    if getattr(state.config_data, 'auto_apply', False):
        logger.info(f"Auto applying to {pj.job.title} at {pj.job.company}")
        client = LinkedInClient()
        success = await client.easy_apply(pj.job.link)
        if success:
            pj.application_status = ApplicationStatus.APPLIED
            state.processing_state.applied_jobs.append(pj)
            logger.info("Application successful!")
        else:
            pj.application_status = ApplicationStatus.FAILED
            pj.error_message = "Easy Apply button missing or failed."
            logger.warning("Application failed.")
    else:
        logger.info(f"Auto-apply disabled. Queuing job {pj.job.job_id}")
        pj.application_status = ApplicationStatus.QUEUED
        
    # Increment job index as this is the end of the loop body
    state.processing_state.current_job_index += 1
    return state
