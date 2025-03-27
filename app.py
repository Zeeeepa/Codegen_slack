import os
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from fastapi import FastAPI
import uvicorn
from threading import Thread

from listeners import register_listeners
from env_loader import load_environment_variables
from github_integration import register_webhook_handler
from agents.agent_registry import AgentRegistry

# Load and normalize environment variables
load_environment_variables()

# Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
logging.basicConfig(level=logging.DEBUG)

# Create FastAPI app
fastapi_app = FastAPI(title="Bolt Chat with Codegen")

# Register Listeners
register_listeners(app)

# Register GitHub webhook handler
register_webhook_handler(app)

# Register default agents
AgentRegistry.register_default_agents()

# Define function to start Bolt app
def start_bolt_app():
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()

# Start Bolt app
if __name__ == "__main__":
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Starting Bolt Chat with Codegen integration")
    logger.info(f"Available agent types: {AgentRegistry.get_agent_types()}")
    
    # Start Bolt app in a separate thread
    bolt_thread = Thread(target=start_bolt_app)
    bolt_thread.daemon = True
    bolt_thread.start()
    
    # Start FastAPI app
    uvicorn.run(fastapi_app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
