"""
Command to list available AI instances.
"""
from slack_bolt import App
from slack_sdk.models.blocks import SectionBlock, MarkdownTextObject, DividerBlock


def register_list_instances_command(app: App):
    """
    Register the list-instances command.
    
    Args:
        app: The Slack app
    """
    @app.command("/list-instances")
    def list_instances_callback(ack, respond, command):
        """
        Handle the list-instances command.
        
        Args:
            ack: Acknowledge function
            respond: Respond function
            command: Command data
        """
        ack()
        
        # This is a placeholder. In a real implementation, you would get the instances from a manager
        instances = [
            {"name": "Default AI", "status": "active", "description": "Default AI provider"},
            {"name": "Codegen", "status": "available", "description": "Code analysis and generation agent"}
        ]
        
        blocks = [
            SectionBlock(
                text=MarkdownTextObject(text="*Available AI Instances*")
            ),
            DividerBlock()
        ]
        
        for instance in instances:
            status_emoji = "🟢" if instance["status"] == "active" else "⚪"
            blocks.append(
                SectionBlock(
                    text=MarkdownTextObject(
                        text=f"{status_emoji} *{instance['name']}*\n{instance['description']}"
                    )
                )
            )
        
        respond(blocks=blocks)