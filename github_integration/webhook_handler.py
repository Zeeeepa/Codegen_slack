import logging
import json
import hmac
import hashlib
import os
from typing import Dict, Any, Optional
from slack_bolt import App
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from .pr_analyzer import analyze_pr

logger = logging.getLogger(__name__)

# GitHub webhook events we're interested in
PR_EVENTS = ["pull_request.opened", "pull_request.synchronize", "pull_request.reopened"]

def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """
    Verify that the webhook payload was sent from GitHub by validating the signature.
    
    Args:
        payload_body: The request body
        signature_header: The GitHub signature header
        
    Returns:
        True if the signature is valid, False otherwise
    """
    if not signature_header:
        return False
        
    webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
    if not webhook_secret:
        logger.warning("GITHUB_WEBHOOK_SECRET not set, skipping signature verification")
        return True
        
    signature_parts = signature_header.split('=')
    if len(signature_parts) != 2:
        return False
        
    algorithm, signature = signature_parts
    if algorithm != 'sha256':
        return False
        
    mac = hmac.new(webhook_secret.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

async def process_github_webhook(request: Request, x_github_event: Optional[str] = Header(None), x_hub_signature_256: Optional[str] = Header(None)):
    """
    Process a GitHub webhook event.
    
    Args:
        request: The FastAPI request
        x_github_event: The GitHub event type
        x_hub_signature_256: The GitHub signature header
    """
    # Get the request body
    payload_body = await request.body()
    
    # Verify the signature
    if not verify_github_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse the payload
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Check if this is a PR event we're interested in
    event_type = x_github_event
    if not event_type:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")
    
    # Get the action from the payload
    action = payload.get("action")
    if not action:
        raise HTTPException(status_code=400, detail="Missing action in payload")
    
    # Combine event and action
    event_action = f"{event_type}.{action}"
    
    # Process PR events
    if event_type == "pull_request" and event_action in PR_EVENTS:
        logger.info(f"Processing PR event: {event_action}")
        
        # Extract PR information
        pr_number = payload.get("number")
        repo_name = payload.get("repository", {}).get("full_name")
        pr_title = payload.get("pull_request", {}).get("title")
        pr_url = payload.get("pull_request", {}).get("html_url")
        
        if not all([pr_number, repo_name, pr_title, pr_url]):
            logger.error("Missing required PR information in payload")
            raise HTTPException(status_code=400, detail="Missing required PR information")
        
        # Analyze the PR
        try:
            analyze_pr(repo_name, pr_number, pr_title, pr_url)
        except Exception as e:
            logger.error(f"Error analyzing PR: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error analyzing PR: {str(e)}")
        
        return {"status": "success", "message": f"Processing PR #{pr_number} from {repo_name}"}
    
    # Ignore other events
    return {"status": "ignored", "message": f"Ignoring event: {event_action}"}

def register_webhook_handler(app: App, fastapi_app: FastAPI):
    """
    Register the GitHub webhook handler with the FastAPI app.
    
    Args:
        app: The Slack Bolt app
        fastapi_app: The FastAPI app
    """
    # Store the Slack app in the FastAPI app state
    fastapi_app.state.slack_app = app
    
    # Register the webhook endpoint
    fastapi_app.post("/github/webhook")(process_github_webhook)
    
    logger.info("Registered GitHub webhook handler")