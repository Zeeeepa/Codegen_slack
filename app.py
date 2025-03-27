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

# Load and normalize environment variables
load_environment_variables()

# Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
logging.basicConfig(level=logging.DEBUG)

# Create FastAPI app
fastapi_app = FastAPI(title="PR Review Agent")

# Register Listeners
register_listeners(app)

# Register GitHub webhook handler
register_webhook_handler(app, fastapi_app)

# Start Bolt app in Socket Mode
def start_bolt_app():
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()

# Start both servers
if __name__ == "__main__":
    # Start Bolt app in a separate thread
    bolt_thread = Thread(target=start_bolt_app)
    bolt_thread.daemon = True
    bolt_thread.start()
    
    # Start FastAPI app
    uvicorn.run(fastapi_app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
