import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure imports work regardless of execution location
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph.graph_builder import build_job_bot_graph
from models.schemas import LinkedInJobBotState, LoginState, Phase
from datetime import datetime

async def main():
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    # Initialize state with user credentials
    initial_state = LinkedInJobBotState(
        login_state=LoginState(
            email=os.getenv('LINKEDIN_EMAIL', 'test@example.com'),
            password=os.getenv('LINKEDIN_PASSWORD', 'testpass'),
            require_2fa=os.getenv('REQUIRE_2FA', 'True').lower() == 'true'
        ),
        current_phase=Phase.INIT,
        start_time=datetime.now()
    )
    
    # Build and compile graph
    graph = build_job_bot_graph()
    
    # Execute workflow
    print("Starting LangGraph Job Bot Workflow execution...\n")
    try:
        final_state = await graph.ainvoke(initial_state)
        # Handle completion
        if final_state.get('current_phase') == Phase.OUTPUT:
            print("\n✅ Workflow completed successfully!")
        else:
            print("\n❌ Workflow failed!")
            print(final_state.get('workflow_error'))
            
    except Exception as e:
        print(f"\n❌ Fatal Graph Execution Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
