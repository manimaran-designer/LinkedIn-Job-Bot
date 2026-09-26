from graph.state import LinkedInJobBotState, ErrorType

def auth_router(state: LinkedInJobBotState) -> str:
    if state.login_state.is_authenticated:
        return 'validate_session'
    
    # If not authenticated
    err = state.login_state.error_type
    if err == ErrorType.TWO_FACTOR:
        return 'handle_2fa'
    elif err == ErrorType.CAPTCHA:
        return 'handle_captcha'
    elif err in [ErrorType.RATE_LIMIT, ErrorType.SESSION_TIMEOUT, ErrorType.NETWORK_ERROR]:
        if state.login_state.retry_count < 3: # max retries
            return 'retry_login'
            
    return 'login_failure'

def filter_router(state: LinkedInJobBotState) -> str:
    idx = state.processing_state.current_job_index
    if idx >= len(state.scraping_state.scraped_jobs):
        return 'aggregate_results' # Emergency fallback if index out of bounds
        
    last_processed = state.processing_state.processed_jobs[-1] if state.processing_state.processed_jobs else None
    
    # If the last processed job is the current job, examine its match status
    # Note: Our filter nodes append to `processed_jobs` as a staging mechanism
    if last_processed and last_processed.job == state.scraping_state.scraped_jobs[idx]:
        if last_processed.is_match:
            return 'process_job' # research/mock_q/customize/apply
        else:
            return 'skip_job'
            
    return 'aggregate_results' # Should not hit

def processor_router(state: LinkedInJobBotState) -> str:
    config = state.config_data
    if not config: return 'apply_job'
    
    if config.need_company_research:
        # Check if already done for current
        last_pj = state.processing_state.processed_jobs[-1]
        if not last_pj.company_info:
            return 'research_company'
            
    if config.prepare_mock_questions:
        last_pj = state.processing_state.processed_jobs[-1]
        if not last_pj.mock_questions:
            return 'mock_questions'
            
    if config.modify_resume:
        last_pj = state.processing_state.processed_jobs[-1]
        if not last_pj.customized_resume:
            return 'customize_resume'
            
    return 'apply_job'

def job_loop_router(state: LinkedInJobBotState) -> str:
    idx = state.processing_state.current_job_index
    jobs = state.scraping_state.scraped_jobs
    
    if idx < len(jobs):
        return 'process_next_job' # Loop back to check_company_blacklist
    else:
        return 'aggregate_results' # Move to Phase 4
