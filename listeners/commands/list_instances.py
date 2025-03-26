import logging
from slack_bolt import App, Ack, Respond
from slack_sdk.web import WebClient
from ai.multi_instance_manager import manager

logger = logging.getLogger(__name__)

def register_list_instances_command(app: App):
    """
    Register the /list-instances command to show available API characters.
    """
    @app.command("/list-instances")
    def handle_list_instances_command(ack: Ack, respond: Respond, client: WebClient):
        ack()
        
        # Get available characters
        openai_characters = manager.get_available_openai_characters()
        anthropic_characters = manager.get_available_anthropic_characters()
        
        # Build response blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Available API Characters",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add OpenAI characters
        if openai_characters:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*OpenAI Characters:*"
                }
            })
            
            character_text = "\n".join([f"• Character: `{character_name}`" for character_name in openai_characters])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": character_text
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*OpenAI Characters:* None available"
                }
            })
        
        # Add Anthropic characters
        if anthropic_characters:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Anthropic Characters:*"
                }
            })
            
            character_text = "\n".join([f"• Character: `{character_name}`" for character_name in anthropic_characters])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": character_text
                }
            })
        else:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Anthropic Characters:* None available"
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
                "text": "*Usage Instructions:*\nTo use a specific character, add the `character` parameter when using the chat commands. For example:\n`/chat character=Sherlock model=gpt-4o Your prompt here`\n`/chat-anthropic character=Watson model=claude-3-opus-20240229 Your prompt here`"
            }
        })
        
        # Send the response
        respond(blocks=blocks)