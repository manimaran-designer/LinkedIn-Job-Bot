from graph.state import LinkedInJobBotState, Phase
from utils.logger import get_logger
import pandas as pd
import os
from datetime import datetime

logger = get_logger('linkedinjobbot.nodes.output')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

async def export_csv_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: export_csv_node ---")
    
    csv_path = os.path.join(BASE_DIR, 'output', 'matched_jobs.csv')
    
    if not state.results_state.final_results:
        logger.warning("No results to export.")
        return state
        
    records = []
    for pj in state.results_state.final_results:
        records.append({
            "JobID": pj.job.job_id,
            "Title": pj.job.title,
            "Company": pj.job.company,
            "Link": pj.job.link,
            "MatchScore": f"{pj.match_score:.1f}%",
            "ApplicationStatus": pj.application_status.value,
            "MissingSkills": ", ".join(pj.skill_gaps)
        })
        
    df = pd.DataFrame(records)
    # Sort descending by match score
    df = df.sort_values(by="MatchScore", ascending=False)
    df.to_csv(csv_path, index=False)
    logger.info(f"Exported matched jobs to {csv_path}")
    
    return state

async def console_summary_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: console_summary_node ---")
    rs = state.results_state
    
    summary = f"""
    ════════════════════════════════════════════════════════
    LinkedIn Job Bot - Execution Summary
    ════════════════════════════════════════════════════════
    Jobs Scraped:     {rs.total_scraped}
    Jobs Matched:     {rs.total_matched} ({(rs.total_matched/rs.total_scraped*100) if rs.total_scraped else 0:.1f}%)
    Jobs Applied:     {rs.total_applied} ({(rs.total_applied/rs.total_matched*100) if rs.total_matched else 0:.1f}%)
    Jobs Skipped:     {rs.total_skipped}
    Success Rate:     {rs.success_rate:.1f}%
    Processing Time:  {rs.processing_time_seconds:.1f} seconds
    
    Output File: output/matched_jobs.csv
    Tracking File: data/applied_jobs.xlsx
    
    Last Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ════════════════════════════════════════════════════════
    """
    print(summary)
    return state

async def return_results_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: return_results_node ---")
    state.current_phase = Phase.OUTPUT
    return state
