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
fastapi_app = FastAPI(title="PR Review Agent")

# Register Listeners
register_listeners(app)

# Register GitHub webhook handler
register_webhook_handler(app)

# Register default agents
AgentRegistry.register_default_agents()

# Define function to start Bolt app
def start_bolt_app():
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()

# Function to select an agent
def select_agent():
    available_agents = AgentRegistry.get_available_agents()
    
    if not available_agents:
        print("No agents available.")
        return None
    
    print("Available agents:")
    for i, agent_name in enumerate(available_agents, 1):
        agent_class = AgentRegistry.get_agent(agent_name)
        print(f"{i}. {agent_name} - {agent_class.get_description()}")
    
    try:
        choice = input("Select an agent (number) or press Enter for default AI: ")
        if not choice.strip():
            print("Using default AI provider.")
            return None
        
        choice = int(choice)
        if 1 <= choice <= len(available_agents):
            selected_agent = available_agents[choice - 1]
            print(f"Selected agent: {selected_agent}")
            os.environ["ACTIVE_AGENT"] = selected_agent
            return selected_agent
        else:
            print("Invalid choice. Using default AI provider.")
            return None
    except ValueError:
        print("Invalid input. Using default AI provider.")
        return None

# Start Bolt app
if __name__ == "__main__":
    # Select an agent
    selected_agent = select_agent()
    
    # Start Bolt app in a separate thread
    bolt_thread = Thread(target=start_bolt_app)
    bolt_thread.daemon = True
    bolt_thread.start()
    
    # Start FastAPI app
    uvicorn.run(fastapi_app, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
