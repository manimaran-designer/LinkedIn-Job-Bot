from langgraph.graph import StateGraph, START, END
from graph.state import LinkedInJobBotState

# Import Phase 0
from graph.nodes.auth_nodes import (
    linkedin_login_node, handle_2fa_node, handle_captcha_node,
    retry_login_node, validate_session_node, login_failure_handler
)
# Import Phase 1
from graph.nodes.load_nodes import load_resume_node, load_config_node, load_blacklist_node
# Import Phase 2
from graph.nodes.scraper_nodes import linkedin_scraper_node
# Import Phase 3
from graph.nodes.filter_nodes import (
    check_company_blacklist_node, check_already_applied_node, skill_matcher_node
)
from graph.nodes.processor_nodes import (
    research_company_node, mock_questions_node, resume_customization_node
)
from graph.nodes.apply_nodes import auto_apply_node
# Import Phase 4
from graph.nodes.tracking_nodes import update_tracking_node, aggregate_results_node
# Import Phase 5
from graph.nodes.output_nodes import export_csv_node, console_summary_node, return_results_node
# Import Edges
from graph.edges import auth_router, filter_router, processor_router, job_loop_router

def build_job_bot_graph() -> StateGraph:
    """Build LangGraph workflow."""
    
    graph = StateGraph(LinkedInJobBotState)
    
    # --- PHASE 0: AUTH ---
    graph.add_node("login_attempt", linkedin_login_node)
    graph.add_node("handle_2fa", handle_2fa_node)
    graph.add_node("handle_captcha", handle_captcha_node)
    graph.add_node("retry_login", retry_login_node)
    graph.add_node("validate_session", validate_session_node)
    graph.add_node("login_failure", login_failure_handler)
    
    # --- PHASE 1: LOAD ---
    graph.add_node("load_resume", load_resume_node)
    graph.add_node("load_config", load_config_node)
    graph.add_node("load_blacklist", load_blacklist_node)
    
    # --- PHASE 2: SCRAPE ---
    graph.add_node("scrape_jobs", linkedin_scraper_node)
    
    # --- PHASE 3: PROCESS LOOP ---
    graph.add_node("check_blacklist", check_company_blacklist_node)
    graph.add_node("check_applied", check_already_applied_node)
    graph.add_node("skill_matching", skill_matcher_node)
    
    graph.add_node("research_company", research_company_node)
    graph.add_node("mock_questions", mock_questions_node)
    graph.add_node("customize_resume", resume_customization_node)
    graph.add_node("apply_job", auto_apply_node)
    
    # --- PHASE 4: TRACKING ---
    graph.add_node("update_tracking", update_tracking_node)
    graph.add_node("aggregate_results", aggregate_results_node)
    
    # --- PHASE 5: OUTPUT ---
    graph.add_node("export_csv", export_csv_node)
    graph.add_node("console_summary", console_summary_node)
    graph.add_node("return_results", return_results_node)
    
    # ==========================
    # --- EDGES AND ROUTING ---
    # ==========================
    
    graph.add_edge(START, "login_attempt")
    graph.add_conditional_edges(
        "login_attempt",
        auth_router,
        {
            'validate_session': 'validate_session',
            'handle_2fa': 'handle_2fa',
            'handle_captcha': 'handle_captcha',
            'retry_login': 'retry_login',
            'login_failure': 'login_failure'
        }
    )
    
    # Return flows for retry and handlers back to attempt or validation
    graph.add_edge("handle_2fa", "validate_session")
    graph.add_edge("handle_captcha", "validate_session")
    graph.add_edge("retry_login", "login_attempt")
    graph.add_edge("login_failure", END)
    
    graph.add_edge("validate_session", "load_resume")
    graph.add_edge("load_resume", "load_config")
    graph.add_edge("load_config", "load_blacklist")
    graph.add_edge("load_blacklist", "scrape_jobs")
    graph.add_edge("scrape_jobs", "check_blacklist")
    
    # --- FILTER SEQUENCE ---
    graph.add_edge("check_blacklist", "check_applied")
    graph.add_edge("check_applied", "skill_matching")
    
    # --- CONDITIONAL PROCESSING ---
    graph.add_conditional_edges(
        "skill_matching",
        filter_router,
        {
            'skip_job': 'update_tracking',
            'process_job': 'research_company',  # First in router chain
            'aggregate_results': 'aggregate_results'
        }
    )
    
    # Loop back logic for the processors
    graph.add_conditional_edges("research_company", processor_router, {
        "mock_questions": "mock_questions",
        "customize_resume": "customize_resume",
        "apply_job": "apply_job"
    })
    
    graph.add_conditional_edges("mock_questions", processor_router, {
        "customize_resume": "customize_resume",
        "apply_job": "apply_job"
    })
    
    graph.add_conditional_edges("customize_resume", processor_router, {
        "apply_job": "apply_job"
    })
    
    graph.add_edge("apply_job", "update_tracking")
    
    # --- CHECK IF LOOP CONTINUES ---
    graph.add_conditional_edges(
        "update_tracking",
        job_loop_router,
        {
            'process_next_job': 'check_blacklist',
            'aggregate_results': 'aggregate_results'
        }
    )
    
    graph.add_edge("aggregate_results", "export_csv")
    graph.add_edge("export_csv", "console_summary")
    graph.add_edge("console_summary", "return_results")
    graph.add_edge("return_results", END)
    
    return graph.compile()
