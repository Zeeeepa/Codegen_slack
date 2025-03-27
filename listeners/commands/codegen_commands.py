"""
Slack commands for interacting with the Codegen agent.
"""

import logging
import json
import asyncio
from typing import Dict, Any

from slack_bolt import App, Ack, BoltContext
from slack_sdk.web import WebClient

from agents.agent_registry import AgentRegistry
from agents.agent_factory import AgentFactory

logger = logging.getLogger(__name__)

async def handle_codegen_command(ack, command, client, context):
    """
    Handle the /codegen command.
    
    This command triggers the Codegen agent to analyze, search, or modify code.
    Format: /codegen [action] [parameters]
    
    Actions:
    - analyze: Analyze code or answer questions about a codebase
    - search: Search for code patterns in a codebase
    - generate: Generate code based on a prompt
    - edit: Edit code based on instructions
    - set-repo: Set the active repository
    """
    # Acknowledge the command
    await ack()
    
    # Extract command parameters
    text = command["text"]
    user_id = command["user_id"]
    channel_id = command["channel_id"]
    
    # Parse the action and parameters
    parts = text.split(maxsplit=1)
    action = parts[0].lower() if parts else "analyze"
    params = parts[1] if len(parts) > 1 else ""
    
    # Send initial response
    response = client.chat_postMessage(
        channel=channel_id,
        text=f"🤖 Processing Codegen {action} request: *{params}*\nI'll get back to you with the results shortly..."
    )
    
    # Create a Codegen agent
    try:
        codegen_agent = AgentFactory.create_agent("codegen")
        
        # Process based on action
        if action == "set-repo":
            result = await codegen_agent.process({
                "action": "set_repo",
                "repo": params
            })
        elif action == "analyze":
            result = await codegen_agent.process({
                "action": "analyze",
                "query": params
            })
        elif action == "search":
            result = await codegen_agent.process({
                "action": "search",
                "query": params
            })
        elif action == "generate":
            result = await codegen_agent.process({
                "action": "generate",
                "prompt": params
            })
        elif action == "edit":
            # Parse edit parameters (file:instructions format)
            if ":" in params:
                file_path, instructions = params.split(":", 1)
                result = await codegen_agent.process({
                    "action": "edit",
                    "file_path": file_path.strip(),
                    "instructions": instructions.strip()
                })
            else:
                result = await codegen_agent.process({
                    "action": "edit",
                    "instructions": params
                })
        else:
            result = {
                "success": False,
                "error": f"Unknown action: {action}",
                "message": f"The action '{action}' is not supported. Use one of: analyze, search, generate, edit, set-repo."
            }
        
        # Format the results
        if result["success"]:
            if action == "set-repo":
                # Format set-repo result
                client.chat_update(
                    channel=channel_id,
                    ts=response["ts"],
                    text=f"✅ Repository set: *{result['repo']}*\n{result['message']}"
                )
            elif action == "analyze":
                # Format analysis result
                client.chat_update(
                    channel=channel_id,
                    ts=response["ts"],
                    text=f"📊 Analysis for: *{result['query']}*\n\n{result['response']}"
                )
            elif action == "search":
                # Format search results
                blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"Search Results: {result['query']}",
                            "emoji": True
                        }
                    }
                ]
                
                if result["results"]:
                    for item in result["results"][:10]:
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{item['file']}* (Line {item['line']})\n```{item['content']}```"
                            }
                        })
                else:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "No results found."
                        }
                    })
                
                client.chat_update(
                    channel=channel_id,
                    ts=response["ts"],
                    text=f"Search results for: {result['query']}",
                    blocks=blocks
                )
            elif action == "generate":
                # Format generation result
                client.chat_update(
                    channel=channel_id,
                    ts=response["ts"],
                    text=f"💻 Generated code for: *{result['prompt']}*\n\n{result['response']}"
                )
            elif action == "edit":
                # Format edit result
                file_info = f" in *{result['file_path']}*" if result.get('file_path') else ""
                client.chat_update(
                    channel=channel_id,
                    ts=response["ts"],
                    text=f"✏️ Code edits{file_info}: *{result['instructions']}*\n\n{result['response']}"
                )
        else:
            # Handle error
            client.chat_update(
                channel=channel_id,
                ts=response["ts"],
                text=f"❌ Error processing {action} request: {result['error']}\n{result['message']}"
            )
    except Exception as e:
        logger.error(f"Error processing codegen command: {str(e)}")
        client.chat_update(
            channel=channel_id,
            ts=response["ts"],
            text=f"❌ Error processing codegen command: {str(e)}"
        )

def register(app: App):
    """
    Register codegen commands with the Slack app.
    """
    app.command("/codegen", handle_codegen_command)
    
    logger.info("Registered codegen commands")