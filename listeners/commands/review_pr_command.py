
"""
Command to manually trigger a PR review.
"""

import logging
import re
from slack_bolt import App, Ack, Say
from github_integration.pr_analyzer import analyze_pull_request
from github_integration.github_api import post_pr_comment, get_pr_details
from github_integration.slack_notifier import notify_pr_analyzed, notify_error

logger = logging.getLogger(__name__)

def review_pr_command(ack, command, say):
    """
    Handle the /review-pr command.
    
    Args:
        ack: Acknowledge function
        command: Command payload
        say: Say function
    """
    ack()
    
    # Parse the command text
    text = command.get("text", "").strip()
    
    # Check if the command text is empty
    if not text:
        say("Please provide a GitHub PR URL or 'repo/owner#pr_number'")
        return
    
    # Try to extract repo and PR number from the text
    repo_name, pr_number = parse_pr_reference(text)
    
    if not repo_name or not pr_number:
        say("Invalid PR reference. Please provide a GitHub PR URL or 'repo/owner#pr_number'")
        return
    
    # Acknowledge the command
    say(f"Analyzing PR #{pr_number} in {repo_name}...")
    
    try:
        # Analyze the PR
        analysis_result = analyze_pull_request(repo_name, pr_number)
        
        # Post the analysis as a comment on the PR
        if analysis_result:
            post_pr_comment(repo_name, pr_number, analysis_result)
            
            # Get PR details for the notification
            pr_details = get_pr_details(repo_name, pr_number)
            pr_title = pr_details.get("title", "")
            pr_url = pr_details.get("html_url", "")
            
            # Send a notification to the channel
            say(
                f"*PR Review Completed* :mag:\n"
                f"Repository: `{repo_name}`\n"
                f"PR #{pr_number}: <{pr_url}|{pr_title}>\n\n"
                f"I've analyzed this PR and provided feedback. Check out my comments on GitHub!"
            )
    except Exception as e:
        logger.error(f"Error analyzing PR: {str(e)}")
        say(f"Error analyzing PR: {str(e)}")

def parse_pr_reference(text):
    """
    Parse a PR reference from text.
    
    Args:
        text: The text to parse
    
    Returns:
        tuple: (repo_name, pr_number) or (None, None) if parsing fails
    """
    # Try to match a GitHub PR URL
    url_pattern = r"https?://github\.com/([^/]+/[^/]+)/pull/(\d+)"
    url_match = re.search(url_pattern, text)
    if url_match:
        return url_match.group(1), int(url_match.group(2))
    
    # Try to match a repo#pr format
    repo_pr_pattern = r"([^/]+/[^#]+)#(\d+)"
    repo_pr_match = re.search(repo_pr_pattern, text)
    if repo_pr_match:
        return repo_pr_match.group(1), int(repo_pr_match.group(2))
    
    return None, None

def register(app: App):
    """
    Register the review-pr command.
    
    Args:
        app: The Bolt app
    """
    app.command("/review-pr")(review_pr_command)
