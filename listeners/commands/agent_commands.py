"""
Slack commands for interacting with agents.
"""

import logging
import json
import asyncio
from typing import Dict, Any

from slack_bolt import App, Ack, BoltContext
from slack_sdk.web import WebClient

from agents.agent_registry import AgentRegistry
from agents.agent_factory import AgentFactory
from agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

# Initialize the orchestrator
orchestrator = AgentOrchestrator()

# Register the default agents
AgentRegistry.register_default_agents()

async def handle_research_command(ack, command, client, context):
    """
    Handle the /research command.
    
    This command triggers the Researcher agent to gather information.
    """
    # Acknowledge the command
    await ack()
    
    # Extract command parameters
    text = command["text"]
    user_id = command["user_id"]
    channel_id = command["channel_id"]
    
    # Send initial response
    response = client.chat_postMessage(
        channel=channel_id,
        text=f"🔍 Researching: *{text}*\nI'll get back to you with the results shortly..."
    )
    
    # Create a researcher agent
    try:
        researcher = AgentFactory.create_agent("researcher")
        
        # Process the research request
        result = await researcher.process({
            "query": text,
            "sources": ["web", "docs", "github"],
            "max_results": 5
        })
        
        # Format the results
        if result["success"]:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Research Results: {text}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{result['summary']}"
                    }
                },
                {
                    "type": "divider"
                }
            ]
            
            # Add result items
            for item in result["results"]["items"][:5]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{item['title']}*\n{item['snippet']}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Source",
                            "emoji": True
                        },
                        "url": item.get("url", "#"),
                        "action_id": "view_source"
                    }
                })
            
            # Update the message
            client.chat_update(
                channel=channel_id,
                ts=response["ts"],
                text=f"Research results for: {text}",
                blocks=blocks
            )
        else:
            # Handle error
            client.chat_update(
                channel=channel_id,
                ts=response["ts"],
                text=f"❌ Error researching: {text}\n{result['error']}"
            )
    except Exception as e:
        logger.error(f"Error processing research command: {str(e)}")
        client.chat_update(
            channel=channel_id,
            ts=response["ts"],
            text=f"❌ Error processing research command: {str(e)}"
        )

async def handle_plan_command(ack, command, client, context):
    """
    Handle the /plan command.
    
    This command triggers the Planner agent to create a structured plan.
    """
    # Acknowledge the command
    await ack()
    
    # Extract command parameters
    text = command["text"]
    user_id = command["user_id"]
    channel_id = command["channel_id"]
    
    # Send initial response
    response = client.chat_postMessage(
        channel=channel_id,
        text=f"📝 Creating plan for: *{text}*\nI'll get back to you with the plan shortly..."
    )
    
    # Create a planner agent
    try:
        planner = AgentFactory.create_agent("planner")
        
        # Process the planning request
        result = await planner.process({
            "task": text,
            "planning_method": "sequential",
            "constraints": [],
            "resources": []
        })
        
        # Format the results
        if result["success"]:
            plan = result["plan"]
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Plan: {text}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Type:* {plan['type']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Estimated Duration:* {plan['estimated_duration']}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Success Criteria:*\n{plan['success_criteria']}"
                    }
                },
                {
                    "type": "divider"
                }
            ]
            
            # Add steps
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Steps:*"
                }
            })
            
            for step in plan.get("steps", []):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{step['step_number']}.* {step['description']}\n_Duration: {step['estimated_duration']}_"
                    }
                })
            
            # Update the message
            client.chat_update(
                channel=channel_id,
                ts=response["ts"],
                text=f"Plan for: {text}",
                blocks=blocks
            )
        else:
            # Handle error
            client.chat_update(
                channel=channel_id,
                ts=response["ts"],
                text=f"❌ Error creating plan: {text}\n{result['error']}"
            )
    except Exception as e:
        logger.error(f"Error processing plan command: {str(e)}")
        client.chat_update(
            channel=channel_id,
            ts=response["ts"],
            text=f"❌ Error processing plan command: {str(e)}"
        )

async def handle_code_command(ack, command, client, context):
    """
    Handle the /code command.
    
    This command triggers the Code Applicator agent to implement code changes.
    """
    # Acknowledge the command
    await ack()
    
    # Extract command parameters
    text = command["text"]
    user_id = command["user_id"]
    channel_id = command["channel_id"]
    
    # Send initial response
    response = client.chat_postMessage(
        channel=channel_id,
        text=f"💻 Implementing code changes: *{text}*\nI'll get back to you with the results shortly..."
    )
    
    # Create a code applicator agent
    try:
        code_applicator = AgentFactory.create_agent("code_applicator")
        
        # Process the code change request
        result = await code_applicator.process({
            "specification": text,
            "language": "python",
            "file_paths": []
        })
        
        # Format the results
        if result["success"]:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Code Changes: {text}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{result['summary']}"
                    }
                },
                {
                    "type": "divider"
                }
            ]
            
            # Add changed files
            for file_change in result["changes"]["files_changed"][:5]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{file_change['file_path']}* ({file_change['status']})"
                    }
                })
                
                if file_change["status"] == "modified" and "diff" in file_change:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"```{file_change['diff']}```"
                        }
                    })
            
            # Update the message
            client.chat_update(
                channel=channel_id,
                ts=response["ts"],
                text=f"Code changes for: {text}",
                blocks=blocks
            )
        else:
            # Handle error
            client.chat_update(
                channel=channel_id,
                ts=response["ts"],
                text=f"❌ Error implementing code changes: {text}\n{result['error']}"
            )
    except Exception as e:
        logger.error(f"Error processing code command: {str(e)}")
        client.chat_update(
            channel=channel_id,
            ts=response["ts"],
            text=f"❌ Error processing code command: {str(e)}"
        )

async def handle_orchestrate_command(ack, command, client, context):
    """
    Handle the /orchestrate command.
    
    This command triggers the Orchestrator to coordinate multiple agents.
    """
    # Acknowledge the command
    await ack()
    
    # Extract command parameters
    text = command["text"]
    user_id = command["user_id"]
    channel_id = command["channel_id"]
    
    # Parse the workflow from the command text
    # Format: agent1:task1|agent2:task2|...
    try:
        workflow_steps = []
        for step in text.split("|"):
            agent_type, task = step.strip().split(":", 1)
            workflow_steps.append({
                "type": "agent",
                "agent_id": agent_type.strip(),
                "input_mapping": {
                    "task": "input.task"
                },
                "output_mapping": {
                    f"result_{agent_type}": "result"
                }
            })
        
        # Create a workflow
        workflow_id = f"workflow_{user_id}_{int(context['request_time'])}"
        workflow = {
            "name": f"Workflow for {user_id}",
            "steps": workflow_steps
        }
        
        # Register the workflow with the orchestrator
        orchestrator.register_workflow(workflow_id, workflow)
        
        # Send initial response
        response = client.chat_postMessage(
            channel=channel_id,
            text=f"🔄 Orchestrating workflow: *{text}*\nI'll get back to you with the results shortly..."
        )
        
        # Process the workflow
        result = await orchestrator.process_task(
            {"task": text},
            workflow_id
        )
        
        # Format the results
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Workflow Results",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Workflow:* {text}"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add results from each agent
        for key, value in result.items():
            if key.startswith("result_"):
                agent_type = key[7:]  # Remove "result_" prefix
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{agent_type.capitalize()} Results:*\n```{json.dumps(value, indent=2)}```"
                    }
                })
        
        # Update the message
        client.chat_update(
            channel=channel_id,
            ts=response["ts"],
            text=f"Workflow results for: {text}",
            blocks=blocks
        )
    except Exception as e:
        logger.error(f"Error processing orchestrate command: {str(e)}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Error processing orchestrate command: {str(e)}\n\nFormat should be: agent1:task1|agent2:task2|..."
        )

def register(app: App):
    """
    Register agent commands with the Slack app.
    """
    app.command("/research", handle_research_command)
    app.command("/plan", handle_plan_command)
    app.command("/code", handle_code_command)
    app.command("/orchestrate", handle_orchestrate_command)
    
    logger.info("Registered agent commands")