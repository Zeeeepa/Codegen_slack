"""
Configuration module for PR review agent.
"""

import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_github_config() -> Dict[str, Any]:
    """
    Get the GitHub configuration from environment variables.
    
    Returns:
        Dict[str, Any]: The GitHub configuration
    """
    # Get the GitHub token
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        logger.warning("GITHUB_TOKEN environment variable is not set")
    
    # Get the webhook secret
    webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
    if not webhook_secret:
        logger.warning("GITHUB_WEBHOOK_SECRET environment variable is not set")
    
    # Get the repositories to monitor
    repos_to_monitor = os.environ.get("PR_REVIEW_REPOS", "").split(",")
    repos_to_monitor = [repo.strip() for repo in repos_to_monitor if repo.strip()]
    
    # If no repositories are specified, monitor all repositories
    if not repos_to_monitor:
        logger.info("No repositories specified, will monitor all repositories")
    else:
        logger.info(f"Monitoring repositories: {', '.join(repos_to_monitor)}")
    
    return {
        "github_token": github_token,
        "webhook_secret": webhook_secret,
        "repos_to_monitor": repos_to_monitor,
    }

def get_ai_config() -> Dict[str, Any]:
    """
    Get the AI configuration from environment variables.
    
    Returns:
        Dict[str, Any]: The AI configuration
    """
    # Get the AI provider
    ai_provider = os.environ.get("PR_REVIEW_AI_PROVIDER", "openai").lower()
    
    # Get the OpenAI configuration
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_model = os.environ.get("PR_REVIEW_OPENAI_MODEL", "gpt-4")
    
    # Get the Anthropic configuration
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    anthropic_model = os.environ.get("PR_REVIEW_ANTHROPIC_MODEL", "claude-3-opus-20240229")
    
    # Log the configuration
    logger.info(f"AI provider: {ai_provider}")
    if ai_provider == "openai":
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY environment variable is not set")
        logger.info(f"OpenAI model: {openai_model}")
    elif ai_provider == "anthropic":
        if not anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY environment variable is not set")
        logger.info(f"Anthropic model: {anthropic_model}")
    
    return {
        "ai_provider": ai_provider,
        "openai_api_key": openai_api_key,
        "openai_model": openai_model,
        "anthropic_api_key": anthropic_api_key,
        "anthropic_model": anthropic_model,
    }

def get_slack_config() -> Dict[str, Any]:
    """
    Get the Slack configuration from environment variables.
    
    Returns:
        Dict[str, Any]: The Slack configuration
    """
    # Get the Slack bot token
    slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_bot_token:
        logger.warning("SLACK_BOT_TOKEN environment variable is not set")
    
    # Get the Slack channel to post notifications to
    slack_channel = os.environ.get("PR_REVIEW_SLACK_CHANNEL", "#general")
    
    return {
        "slack_bot_token": slack_bot_token,
        "slack_channel": slack_channel,
    }

def should_monitor_repo(repo_name: str) -> bool:
    """
    Check if a repository should be monitored.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
    
    Returns:
        bool: True if the repository should be monitored, False otherwise
    """
    repos_to_monitor = get_github_config()["repos_to_monitor"]
    
    # If no repositories are specified, monitor all repositories
    if not repos_to_monitor:
        return True
    
    # Check if the repository is in the list of repositories to monitor
    return repo_name in repos_to_monitor