import logging
import re
from slack_bolt import App, Ack, Respond
from slack_sdk.web import WebClient
from github_integration.pr_analyzer import analyze_pr

logger = logging.getLogger(__name__)

def register_review_pr_command(app: App):
    """
    Register the /review-pr command to manually trigger PR reviews.
    """
    @app.command("/review-pr")
    def handle_review_pr_command(ack: Ack, respond: Respond, command: dict, client: WebClient):
        ack()
        
        # Parse the command text
        text = command.get("text", "").strip()
        
        # Check if the text is empty
        if not text:
            respond({
                "response_type": "ephemeral",
                "text": "Please provide a PR URL or a repository name and PR number. For example: `/review-pr https://github.com/owner/repo/pull/123` or `/review-pr owner/repo 123`"
            })
            return
        
        # Try to parse as a URL
        url_match = re.match(r'https?://github\.com/([^/]+/[^/]+)/pull/(\d+)', text)
        if url_match:
            repo_name = url_match.group(1)
            pr_number = int(url_match.group(2))
            pr_url = text
        else:
            # Try to parse as repo_name and pr_number
            parts = text.split()
            if len(parts) == 2 and '/' in parts[0] and parts[1].isdigit():
                repo_name = parts[0]
                pr_number = int(parts[1])
                pr_url = f"https://github.com/{repo_name}/pull/{pr_number}"
            else:
                respond({
                    "response_type": "ephemeral",
                    "text": "Invalid format. Please provide a PR URL or a repository name and PR number. For example: `/review-pr https://github.com/owner/repo/pull/123` or `/review-pr owner/repo 123`"
                })
                return
        
        # Respond that we're analyzing the PR
        respond({
            "response_type": "in_channel",
            "text": f"Analyzing PR #{pr_number} from {repo_name}... This may take a few minutes."
        })
        
        try:
            # Get PR title
            import requests
            import os
            
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                respond({
                    "response_type": "ephemeral",
                    "text": "GITHUB_TOKEN environment variable not set. Please set it to access the GitHub API."
                })
                return
            
            url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            pr_data = response.json()
            pr_title = pr_data.get("title", f"PR #{pr_number}")
            
            # Analyze the PR
            analyze_pr(repo_name, pr_number, pr_title, pr_url)
            
            # Respond that we've analyzed the PR
            respond({
                "response_type": "in_channel",
                "text": f"I've reviewed PR #{pr_number} from {repo_name}: {pr_title}\n{pr_url}"
            })
        except Exception as e:
            logger.error(f"Error analyzing PR: {str(e)}")
            respond({
                "response_type": "ephemeral",
                "text": f"Error analyzing PR: {str(e)}"
            })