from graph.state import LinkedInJobBotState, ErrorType, Phase
from utils.logger import get_logger
from utils.linkedin_client import LinkedInClient
from datetime import datetime
import asyncio

logger = get_logger('linkedinjobbot.nodes.auth')

async def linkedin_login_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    """Attempt LinkedIn login with email/password."""
    logger.info("--- NODE: linkedin_login_node ---")
    login_state = state.login_state
    
    client = LinkedInClient()
    try:
        res = await client.login(login_state.email, login_state.password)
        login_state.is_authenticated = res.get("is_authenticated", False)
        
        if login_state.is_authenticated:
            login_state.session_token = res.get("session_token")
            login_state.csrf_token = res.get("csrf_token")
            login_state.cookies = res.get("cookies", {})
            login_state.login_timestamp = datetime.now()
            logger.info("Login successful")
        else:
            login_state.error_type = ErrorType.INVALID_CREDS
            logger.warning("Invalid Credentials")
            
    except Exception as e:
        logger.error(f"Login Attempt Failed: {e}")
        login_state.error_type = ErrorType.NETWORK_ERROR
        login_state.last_error = str(e)
        
    state.current_phase = Phase.AUTH
    return state

async def handle_2fa_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: handle_2fa_node ---")
    # Mocking manual 2FA entry by simulating success
    state.login_state.is_authenticated = True
    return state

async def handle_captcha_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: handle_captcha_node ---")
    # Mocking captcha solve
    state.login_state.error_type = None
    return state

async def retry_login_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: retry_login_node ---")
    state.login_state.retry_count += 1
    await asyncio.sleep(2) # Backoff
    return state

async def validate_session_node(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: validate_session_node ---")
    # If we made it here, auth is considered successful
    return state

async def login_failure_handler(state: LinkedInJobBotState) -> LinkedInJobBotState:
    logger.info("--- NODE: login_failure_handler ---")
    state.login_state.is_authenticated = False
    state.current_phase = Phase.FAILED
    state.workflow_error = "Maximum login retries exceeded or fatal error."
    return state
