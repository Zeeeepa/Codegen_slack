import logging
from slack_bolt import App, Ack, Respond
from slack_sdk.web import WebClient
from ai.multi_instance_manager import manager

logger = logging.getLogger(__name__)

def register_list_instances_command(app: App):
    """
    Register the /list-instances command to show available API instances.
    """
    @app.command("/list-instances")
    def handle_list_instances_command(ack: Ack, respond: Respond, client: WebClient):
        ack()
        
        # Get available instances
        openai_instances = manager.get_available_openai_instances()
        anthropic_instances = manager.get_available_anthropic_instances()
        
        # Build response blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Available API Instances",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add OpenAI instances
        if openai_instances:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*OpenAI Instances:*"
                }
            })
            
            instance_text = "\n".join([f"• Instance ID: `{instance_id}`" for instance_id in openai_instances])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": instance_text
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*OpenAI Instances:* None available"
                }
            })
        
        # Add Anthropic instances
        if anthropic_instances:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Anthropic Instances:*"
                }
            })
            
            instance_text = "\n".join([f"• Instance ID: `{instance_id}`" for instance_id in anthropic_instances])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": instance_text
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Anthropic Instances:* None available"
                }
            })
        
        # Add usage instructions
        blocks.append({
            "type": "divider"
        })
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Usage Instructions:*\nTo use a specific instance, add the `instance_id` parameter when using the chat commands. For example:\n`/chat-openai instance_id=1 model=gpt-4o Your prompt here`\n`/chat-anthropic instance_id=2 model=claude-3-opus-20240229 Your prompt here`"
            }
        })
        
        # Send the response
        respond(blocks=blocks)