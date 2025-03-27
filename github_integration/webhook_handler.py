"""
GitHub webhook handler for PR review agent.
"""

import json
import logging
import os
import hmac
import hashlib
from slack_bolt import App, BoltRequest, BoltResponse
from github_integration.pr_analyzer import analyze_pull_request
from github_integration.github_api import post_pr_comment, get_pr_details
from github_integration.slack_notifier import notify_pr_analyzed, notify_error
from github_integration.config import should_monitor_repo

logger = logging.getLogger(__name__)

def register_webhook_handler(app: App):
    """
    Register the GitHub webhook handler with the Bolt app.
    
    Args:
        app: The Bolt app instance
    """
    @app.route("/github/webhook", methods=["POST"])
    def handle_github_webhook(req: BoltRequest) -> BoltResponse:
        # Verify webhook signature if a secret is configured
        if not verify_webhook_signature(req):
            logger.error("Invalid webhook signature")
            return BoltResponse(status=401, body=json.dumps({"error": "Invalid signature"}))
        
        # Parse the webhook payload
        try:
            payload = json.loads(req.body)
        except json.JSONDecodeError:
            logger.error("Failed to parse webhook payload")
            return BoltResponse(status=400, body=json.dumps({"error": "Invalid JSON payload"}))
        
        # Check if this is a pull request event
        if req.headers.get("X-GitHub-Event") == "pull_request":
            return handle_pull_request_event(payload)
        
        # Return a 200 response for other events
        return BoltResponse(status=200, body=json.dumps({"message": "Event received but not processed"}))

def verify_webhook_signature(req: BoltRequest) -> bool:
    """
    Verify the GitHub webhook signature.
    
    Args:
        req: The Bolt request
    
    Returns:
        bool: True if the signature is valid, False otherwise
    """
    webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
    if not webhook_secret:
        # If no secret is configured, skip verification
        return True
    
    signature_header = req.headers.get("X-Hub-Signature-256")
    if not signature_header:
        return False
    
    # Calculate the expected signature
    expected_signature = "sha256=" + hmac.new(
        webhook_secret.encode("utf-8"),
        req.body.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures using a constant-time comparison
    return hmac.compare_digest(signature_header, expected_signature)

def handle_pull_request_event(payload):
    """
    Handle a pull request event from GitHub.
    
    Args:
        payload: The webhook payload
    
    Returns:
        BoltResponse: The response to send back to GitHub
    """
    # Extract PR information
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    
    # Only process opened or synchronize (updated) events
    if action not in ["opened", "synchronize"]:
        return BoltResponse(status=200, body=json.dumps({"message": f"PR {action} event ignored"}))
    
    pr_number = pr.get("number")
    repo_name = repo.get("full_name")
    
    if not pr_number or not repo_name:
        logger.error("Missing PR number or repo name in webhook payload")
        return BoltResponse(status=400, body=json.dumps({"error": "Missing PR information"}))
    
    # Check if we should monitor this repository
    if not should_monitor_repo(repo_name):
        logger.info(f"Ignoring PR #{pr_number} in {repo_name} (not in monitored repositories)")
        return BoltResponse(status=200, body=json.dumps({"message": "Repository not monitored"}))
    
    logger.info(f"Processing PR #{pr_number} in {repo_name}")
    
    try:
        # Analyze the PR
        analysis_result = analyze_pull_request(repo_name, pr_number)
        
        # Post the analysis as a comment on the PR
        if analysis_result:
            post_pr_comment(repo_name, pr_number, analysis_result)
            logger.info(f"Posted analysis for PR #{pr_number} in {repo_name}")
            
            # Send a notification to Slack
            pr_details = get_pr_details(repo_name, pr_number)
            pr_title = pr_details.get("title", "")
            pr_url = pr_details.get("html_url", "")
            notify_pr_analyzed(repo_name, pr_number, pr_title, pr_url)
        
        return BoltResponse(status=200, body=json.dumps({"message": "PR analyzed successfully"}))
    except Exception as e:
        logger.error(f"Error processing PR: {str(e)}")
        
        # Send an error notification to Slack
        notify_error(repo_name, pr_number, str(e))
        
        return BoltResponse(status=500, body=json.dumps({"error": f"Error processing PR: {str(e)}"}))