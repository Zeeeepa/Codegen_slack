"""
Commands for interacting with agents.
"""
import logging
import os
from slack_bolt import App
from agents.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)

def register(app: App):
    """
    Register agent commands with the Slack app.
    
    Args:
        app: The Slack app
    """
    @app.command("/agent")
    def agent_command(ack, respond, command):
        """
        Handle the agent command.
        
        Args:
            ack: Acknowledge function
            respond: Respond function
            command: Command data
        """
        ack()
        
        # Parse the command text
        text = command.get("text", "").strip()
        
        if not text:
            # Show available agents
            available_agents = AgentRegistry.get_available_agents()
            if not available_agents:
                respond("No agents are currently available.")
                return
                
            response = "*Available Agents:*\n"
            for agent_name in available_agents:
                agent_class = AgentRegistry.get_agent(agent_name)
                response += f"• *{agent_name}*: {agent_class.get_description()}\n"
                
            respond(response)
            return
            
        # Check if the first word is a command
        parts = text.split(maxsplit=1)
        subcommand = parts[0].lower()
        
        if subcommand == "use":
            if len(parts) < 2:
                respond("Please specify an agent name. Example: `/agent use codegen`")
                return
                
            agent_name = parts[1].lower()
            try:
                # Check if the agent exists
                AgentRegistry.get_agent(agent_name)
                
                # Set the active agent
                os.environ["ACTIVE_AGENT"] = agent_name
                respond(f"Active agent set to *{agent_name}*")
            except ValueError as e:
                respond(f"Error: {str(e)}")
        elif subcommand == "info":
            if len(parts) < 2:
                respond("Please specify an agent name. Example: `/agent info codegen`")
                return
                
            agent_name = parts[1].lower()
            try:
                agent_class = AgentRegistry.get_agent(agent_name)
                respond(f"*{agent_name}*: {agent_class.get_description()}")
            except ValueError as e:
                respond(f"Error: {str(e)}")
        else:
            # Process the message with the active agent
            active_agent_name = os.environ.get("ACTIVE_AGENT")
            if not active_agent_name:
                respond("No active agent set. Use `/agent use <agent_name>` to set an active agent.")
                return
                
            try:
                agent_class = AgentRegistry.get_agent(active_agent_name)
                agent = agent_class()
                
                # Process the message
                response = agent.process_message(text)
                respond(response)
            except Exception as e:
                logger.error(f"Error processing message with agent: {e}")
                respond(f"Error processing message with agent: {str(e)}")