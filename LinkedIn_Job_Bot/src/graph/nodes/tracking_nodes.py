from graph.state import LinkedInJobBotState, Phase
from utils.logger import get_logger
import pandas as pd
import os
from datetime import datetime

logger = get_logger('linkedinjobbot.nodes.tracking')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

async def update_tracking_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: update_tracking_node ---")
    
    excel_path = os.path.join(BASE_DIR, 'data', 'applied_jobs.xlsx')
    
    processed_jobs = state.processing_state.processed_jobs
    if not processed_jobs:
        logger.warning("No processed jobs to track.")
        return state
        
    records = []
    for pj in processed_jobs:
        records.append({
            "JobID": pj.job.job_id,
            "Title": pj.job.title,
            "Company": pj.job.company,
            "Link": pj.job.link,
            "MatchScore": pj.match_score,
            "ApplicationStatus": pj.application_status.value,
            "ApplicationDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S") if pj.application_status.value == "Applied" else None,
            "MissingSkills": ", ".join(pj.skill_gaps)
        })
        
    df_new = pd.DataFrame(records)
    
    try:
        if os.path.exists(excel_path):
            df_existing = pd.read_excel(excel_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_excel(excel_path, index=False)
        else:
            df_new.to_excel(excel_path, index=False)
        logger.info(f"Updated tracking spreadsheet at {excel_path}")
    except Exception as e:
        logger.error(f"Failed to save tracking info: {e}")
        
    state.current_phase = Phase.AGGREGATE
    return state

async def aggregate_results_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: aggregate_results_node ---")
    
    scraped = state.scraping_state.total_jobs_scraped
    matched = len(state.processing_state.matched_jobs)
    applied = len(state.processing_state.applied_jobs)
    skipped = len(state.processing_state.skipped_jobs)
    
    success_rate = (applied / matched * 100) if matched > 0 else 0.0
    
    state.results_state.total_scraped = scraped
    state.results_state.total_matched = matched
    state.results_state.total_applied = applied
    state.results_state.total_skipped = skipped
    state.results_state.success_rate = success_rate
    
    runtime = (datetime.now() - state.start_time).total_seconds()
    state.results_state.processing_time_seconds = runtime
    state.results_state.final_results = state.processing_state.processed_jobs
    
    logger.info(f"Aggregated {matched} matched jobs out of {scraped} scraped.")
    return state
