from graph.state import LinkedInJobBotState, Phase
from utils.logger import get_logger
from utils.linkedin_client import LinkedInClient

logger = get_logger('linkedinjobbot.nodes.scraper')

async def linkedin_scraper_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: linkedin_scraper_node ---")
    config = state.config_data
    
    if not config:
        logger.error("Configuration not loaded.")
        state.workflow_error = "Missing ConfigData."
        return state

    client = LinkedInClient(
        session_token=state.login_state.session_token,
        cookies=state.login_state.cookies
    )
    
    try:
        jobs = await client.scrape_jobs(
            keywords=config.search_keywords,
            filters={"location": config.location_filter, "job_type": "Full-time"}
        )
        
        state.scraping_state.scraped_jobs = jobs
        state.scraping_state.total_jobs_scraped = len(jobs)
        logger.info(f"Successfully scraped {len(jobs)} jobs.")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        state.scraping_state.scraping_error = str(e)
        state.workflow_error = str(e)

    state.current_phase = Phase.SCRAPE
    return state
