"""
Slack commands for LangChain and Codegen agents.
"""

import logging
import os
from typing import Dict, Any

from slack_bolt import App
from agents.agent_factory import AgentFactory

logger = logging.getLogger(__name__)

def register_langchain_commands(app: App) -> None:
    """
    Register Slack commands for LangChain and Codegen agents.
    
    Args:
        app: The Slack Bolt app
    """
    @app.command("/langchain")
    async def handle_langchain_command(ack, command, client, respond):
        """
        Handle the /langchain command.
        
        This command allows users to interact with the LangChain agent.
        """
        await ack()
        
        try:
            # Extract command text
            text = command["text"]
            user_id = command["user_id"]
            channel_id = command["channel_id"]
            
            # Create a LangChain agent
            agent = AgentFactory.create_agent("langchain")
            
            # Send initial response
            await respond(f"Processing your request with LangChain: `{text}`")
            
            # Process the request
            result = await agent.process({
                "prompt": text,
                "system_prompt": "You are a helpful assistant that answers questions concisely and accurately."
            })
            
            # Send the result
            if result.get("success", False):
                await respond(result.get("result", "No result"))
            else:
                await respond(f"Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error handling langchain command: {str(e)}")
            await respond(f"Error: {str(e)}")
    
    @app.command("/codegen")
    async def handle_codegen_command(ack, command, client, respond):
        """
        Handle the /codegen command.
        
        This command allows users to interact with the Codegen agent.
        """
        await ack()
        
        try:
            # Extract command text
            text = command["text"]
            user_id = command["user_id"]
            channel_id = command["channel_id"]
            
            # Parse the command
            parts = text.split(" ", 1)
            if len(parts) < 2:
                await respond("Usage: /codegen [action] [query]\nActions: analyze, generate, search, edit")
                return
                
            action = parts[0].lower()
            query = parts[1]
            
            # Create a Codegen agent
            agent = AgentFactory.create_agent("codegen")
            
            # Send initial response
            await respond(f"Processing your {action} request with Codegen: `{query}`")
            
            # Process the request
            if action == "analyze":
                result = await agent.process({
                    "action": "analyze",
                    "code": query
                })
            elif action == "generate":
                result = await agent.process({
                    "action": "generate",
                    "query": query
                })
            elif action == "search":
                result = await agent.process({
                    "action": "search",
                    "query": query
                })
            elif action == "edit":
                # Parse edit instructions and code
                edit_parts = query.split("---", 1)
                if len(edit_parts) < 2:
                    await respond("Usage for edit: /codegen edit [instructions] --- [code]")
                    return
                    
                instructions = edit_parts[0].strip()
                code = edit_parts[1].strip()
                
                result = await agent.process({
                    "action": "edit",
                    "code": code,
                    "edit_instructions": instructions
                })
            else:
                await respond(f"Unknown action: {action}\nSupported actions: analyze, generate, search, edit")
                return
            
            # Send the result
            if result.get("success", False):
                if action == "analyze":
                    await respond(f"Analysis result:\n```\n{result.get('analysis', {})}\n```")
                elif action == "generate":
                    await respond(f"Generated code:\n```\n{result.get('generated_code', '')}\n```")
                elif action == "search":
                    search_results = result.get('search_results', [])
                    response = "Search results:\n"
                    for i, item in enumerate(search_results[:5]):
                        response += f"{i+1}. {item.get('file', '')}: {item.get('snippet', '')}\n"
                    await respond(response)
                elif action == "edit":
                    await respond(f"Edited code:\n```\n{result.get('edited_code', '')}\n```")
            else:
                await respond(f"Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error handling codegen command: {str(e)}")
            await respond(f"Error: {str(e)}")
    
    logger.info("Registered LangChain and Codegen commands")