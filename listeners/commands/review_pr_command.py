"""
Command for reviewing GitHub pull requests.
"""
import logging
import re
from slack_bolt import App
from slack_sdk.models.blocks import SectionBlock, MarkdownTextObject, DividerBlock

logger = logging.getLogger(__name__)

def register(app: App):
    """
    Register the review-pr command.
    
    Args:
        app: The Slack app
    """
    @app.command("/review-pr")
    def review_pr_command(ack, respond, command):
        """
        Handle the review-pr command.
        
        Args:
            ack: Acknowledge function
            respond: Respond function
            command: Command data
        """
        ack()
        
        # Parse the command text
        text = command.get("text", "").strip()
        
        if not text:
            respond("Please provide a GitHub PR URL. Example: `/review-pr https://github.com/Zeeeepa/bolt-chat/pull/1`")
            return
            
        # Extract PR information from URL
        pr_info = extract_pr_info(text)
        if not pr_info:
            respond("Invalid GitHub PR URL. Please provide a valid URL like: `https://github.com/Zeeeepa/bolt-chat/pull/1`")
            return
            
        # Acknowledge the request
        respond(f"I'll review PR #{pr_info['pr_number']} in the {pr_info['owner']}/{pr_info['repo']} repository. This may take a few minutes...")
        
        # In a real implementation, you would trigger the PR review process here
        # For now, we'll just respond with a placeholder message
        blocks = [
            SectionBlock(
                text=MarkdownTextObject(text=f"*PR Review: {pr_info['owner']}/{pr_info['repo']}#{pr_info['pr_number']}*")
            ),
            DividerBlock(),
            SectionBlock(
                text=MarkdownTextObject(text="This is a placeholder for the PR review. In a real implementation, this would contain the actual review.")
            )
        ]
        
        respond(blocks=blocks)

def extract_pr_info(url):
    """
    Extract PR information from a GitHub URL.
    
    Args:
        url: The GitHub PR URL
        
    Returns:
        A dictionary with PR information, or None if the URL is invalid
    """
    # Match GitHub PR URLs like https://github.com/owner/repo/pull/123
    pattern = r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.match(pattern, url)
    
    if not match:
        return None
        
    return {
        "owner": match.group(1),
        "repo": match.group(2),
        "pr_number": match.group(3)
    }