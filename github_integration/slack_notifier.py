"""
Slack notification module for PR review agent.
"""

import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

logger = logging.getLogger(__name__)

def get_slack_client():
    """
    Get a Slack client instance.
    
    Returns:
        WebClient: A Slack client instance
    """
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN environment variable is not set")
    return WebClient(token=token)

def notify_pr_analyzed(repo_name: str, pr_number: int, pr_title: str, pr_url: str):
    """
    Send a notification to Slack when a PR has been analyzed.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
        pr_number: The number of the pull request
        pr_title: The title of the pull request
        pr_url: The URL of the pull request
    """
    client = get_slack_client()
    channel = os.environ.get("PR_REVIEW_SLACK_CHANNEL", "#general")
    
    try:
        message = (
            f"*PR Review Completed* :mag:\n"
            f"Repository: `{repo_name}`\n"
            f"PR #{pr_number}: <{pr_url}|{pr_title}>\n\n"
            f"I've analyzed this PR and provided feedback. Check out my comments on GitHub!"
        )
        
        client.chat_postMessage(
            channel=channel,
            text=message,
            unfurl_links=True
        )
        
        logger.info(f"Sent Slack notification for PR #{pr_number} in {repo_name}")
    except SlackApiError as e:
        logger.error(f"Error sending Slack notification: {e.response['error']}")

def notify_error(repo_name: str, pr_number: int, error_message: str):
    """
    Send an error notification to Slack.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
        pr_number: The number of the pull request
        error_message: The error message
    """
    client = get_slack_client()
    channel = os.environ.get("PR_REVIEW_SLACK_CHANNEL", "#general")
    
    try:
        message = (
            f"*PR Review Error* :warning:\n"
            f"Repository: `{repo_name}`\n"
            f"PR #{pr_number}\n\n"
            f"Error: {error_message}"
        )
        
        client.chat_postMessage(
            channel=channel,
            text=message
        )
        
        logger.info(f"Sent error notification for PR #{pr_number} in {repo_name}")
    except SlackApiError as e:
        logger.error(f"Error sending Slack notification: {e.response['error']}")