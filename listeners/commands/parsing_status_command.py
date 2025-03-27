"""
Command to check the parsing status of the Codegen agent.
"""
import logging
import os
from slack_bolt import App
from slack_sdk.errors import SlackApiError

from agents.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)

def parsing_status_callback(ack, command, client, respond):
    """
    Handle the /parsing-status command.
    
    Args:
        ack: Acknowledge function
        command: Command data
        client: Slack client
        respond: Response function
    """
    # Acknowledge the command
    ack()
    
    try:
        # Get the active agent name from environment variables
        active_agent = os.environ.get("ACTIVE_AGENT")
        
        if not active_agent or active_agent != "codegen":
            respond("No active Codegen agent found. Please select the Codegen agent when starting the application.")
            return
        
        # Get the Codegen agent
        agent_class = AgentRegistry.get_agent("codegen")
        agent = agent_class()
        
        # Get the parsing status
        status = agent.get_parsing_status()
        
        # Format the response based on the status
        if status["status"] == "not_started":
            response = f"Repository parsing has not started for `{status['repo']}`."
        elif status["status"] == "in_progress":
            response = f"Repository parsing is in progress for `{status['repo']}`. Please wait..."
        elif status["status"] == "completed":
            response = f"Repository parsing completed successfully for `{status['repo']}`."
        elif status["status"] == "failed":
            response = (
                f"Repository parsing failed for `{status['repo']}` with error: {status['error']}\n\n"
                f"You can ask the agent to 'retry parsing' to attempt again."
            )
        else:
            response = f"Unknown parsing status: {status['status']}"
        
        # Send the response
        respond(response)
    except Exception as e:
        logger.error(f"Error handling parsing-status command: {e}")
        respond(f"Error checking parsing status: {str(e)}")

def register(app: App):
    """
    Register the parsing-status command.
    
    Args:
        app: The Slack app
    """
    app.command("/parsing-status")(parsing_status_callback)