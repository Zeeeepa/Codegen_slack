"""
PR analyzer for GitHub PR review agent.
"""

import os
import logging
import base64
from typing import Dict, List, Any, Optional, Tuple
import anthropic
import openai
import requests
from github_integration.github_api import get_pr_details, get_pr_files
from github_integration.deep_code_research import DeepCodeResearcher

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"

def get_github_token():
    """
    Get the GitHub token from environment variables.
    
    Returns:
        str: The GitHub token
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    return token

def get_file_content(repo_name: str, file_path: str, ref: str) -> str:
    """
    Get the content of a file from GitHub.
    
    Args:
        repo_name: The repository name (e.g., "owner/repo")
        file_path: The path to the file
        ref: The git reference (branch, commit, etc.)
    
    Returns:
        The content of the file
    """
    token = get_github_token()
    url = f"{GITHUB_API_BASE}/repos/{repo_name}/contents/{file_path}?ref={ref}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    content_data = response.json()
    if "content" in content_data:
        import base64
        return base64.b64decode(content_data["content"]).decode("utf-8")
    
    raise ValueError(f"Could not get content for {file_path}")

def get_pr_diff(repo_name: str, pr_number: int) -> str:
    """
    Get the diff of a PR.
    
    Args:
        repo_name: The repository name (e.g., "owner/repo")
        pr_number: The PR number
    
    Returns:
        The diff of the PR
    """
    token = get_github_token()
    url = f"{GITHUB_API_BASE}/repos/{repo_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.text

def get_pr_details(repo_name: str, pr_number: int) -> Dict[str, Any]:
    """
    Get the details of a PR.
    
    Args:
        repo_name: The repository name (e.g., "owner/repo")
        pr_number: The PR number
    
    Returns:
        The details of the PR
    """
    token = get_github_token()
    url = f"{GITHUB_API_BASE}/repos/{repo_name}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

def create_pr_comment(repo_name: str, pr_number: int, comment: str) -> Dict[str, Any]:
    """
    Create a comment on a PR.
    
    Args:
        repo_name: The repository name (e.g., "owner/repo")
        pr_number: The PR number
        comment: The comment text
    
    Returns:
        The created comment
    """
    token = get_github_token()
    url = f"{GITHUB_API_BASE}/repos/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "body": comment
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json()

def create_pr_review(repo_name: str, pr_number: int, comments: List[Dict[str, Any]], body: str) -> Dict[str, Any]:
    """
    Create a review on a PR.
    
    Args:
        repo_name: The repository name (e.g., "owner/repo")
        pr_number: The PR number
        comments: The review comments
        body: The review body
    
    Returns:
        The created review
    """
    token = get_github_token()
    url = f"{GITHUB_API_BASE}/repos/{repo_name}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "body": body,
        "event": "COMMENT",
        "comments": comments
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    return response.json()

def analyze_code_with_ai(code: str, file_path: str, diff: Optional[str] = None) -> str:
    """
    Analyze code using AI and provide improvement suggestions.
    
    Args:
        code: The code to analyze
        file_path: The path to the file
        diff: The diff of the file (optional)
    
    Returns:
        The analysis result
    """
    # Determine the file type
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Create a prompt for the AI
    prompt = f"""
You are an expert code reviewer. Analyze the following code and provide specific, actionable improvement suggestions.
Always find at least 3 ways to improve the code, even if it looks good. Focus on:

1. Code quality and best practices
2. Performance optimizations
3. Security considerations
4. Readability and maintainability
5. Potential bugs or edge cases

File path: {file_path}
File type: {file_extension}

"""
    
    if diff:
        prompt += f"""
Diff:
```
{diff}
```

"""
    
    prompt += f"""
Code:
```
{code}
```

Provide your analysis in the following format:
## Code Review: [File Name]

### Strengths
- [List at least 2 strengths of the code]

### Improvement Suggestions
1. [First suggestion with specific code example]
2. [Second suggestion with specific code example]
3. [Third suggestion with specific code example]
...

### Summary
[Brief summary of your review and the most important improvements]
"""
    
    # Use OpenAI or Anthropic to generate a response
    try:
        # Try OpenAI first
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            client = openai.OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer. Always provide specific, actionable suggestions for improvement, even if the code looks good."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Error using OpenAI for code analysis: {str(e)}")
    
    try:
        # Fall back to Anthropic
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            response = client.messages.create(
                model="claude-3-opus-20240229",
                system="You are an expert code reviewer. Always provide specific, actionable suggestions for improvement, even if the code looks good.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
    except Exception as e:
        logger.warning(f"Error using Anthropic for code analysis: {str(e)}")
    
    raise ValueError("No AI provider available for code analysis")

def analyze_pr(repo_name: str, pr_number: int, pr_title: str, pr_url: str) -> None:
    """
    Analyze a PR and post a review.
    
    Args:
        repo_name: The repository name (e.g., "owner/repo")
        pr_number: The PR number
        pr_title: The PR title
        pr_url: The PR URL
    """
    logger.info(f"Analyzing PR #{pr_number} from {repo_name}: {pr_title}")
    
    try:
        # Get PR details
        pr_details = get_pr_details(repo_name, pr_number)
        pr_head_sha = pr_details["head"]["sha"]
        pr_description = pr_details.get("body", "")
        
        # Get PR files
        pr_files = get_pr_files(repo_name, pr_number)
        
        # Get PR diff
        pr_diff = get_pr_diff(repo_name, pr_number)
        
        # Initialize deep code researcher
        deep_researcher = DeepCodeResearcher(repo_name, pr_number)
        deep_research_successful = deep_researcher.initialize()
        
        # Analyze each file
        file_analyses = []
        for file in pr_files:
            file_path = file["filename"]
            file_status = file["status"]
            
            # Skip deleted files
            if file_status == "removed":
                continue
            
            # Get file content
            try:
                file_content = get_file_content(repo_name, file_path, pr_head_sha)
                
                # Get file diff
                file_diff = None
                for diff_section in pr_diff.split("diff --git "):
                    if f" a/{file_path} " in diff_section or f" b/{file_path} " in diff_section:
                        file_diff = diff_section
                        break
                
                # Analyze the file
                analysis = analyze_code_with_ai(file_content, file_path, file_diff)
                file_analyses.append((file_path, analysis))
                
                logger.info(f"Analyzed file: {file_path}")
            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {str(e)}")
        
        # Create a summary of all analyses
        summary = f"# PR Review: {pr_title}\n\n"
        summary += "I've analyzed your pull request and have some suggestions for improvement. Even though your code looks good, here are some ways to make it even better:\n\n"
        
        for file_path, analysis in file_analyses:
            summary += f"## File: {file_path}\n\n"
            summary += analysis.strip() + "\n\n"
        
        # Add deep code research insights if available
        if deep_research_successful:
            try:
                deep_insights = deep_researcher.research_pr_changes(pr_files, pr_description)
                summary += "\n\n## Deep Code Research Insights\n\n"
                summary += deep_insights.strip() + "\n\n"
                logger.info("Added deep code research insights to PR review")
            except Exception as e:
                logger.error(f"Error getting deep code research insights: {str(e)}")
        
        summary += "\nThis review was generated automatically by the PR Review Agent. If you have any questions or need clarification, please let me know!"
        
        # Post the review as a comment
        create_pr_comment(repo_name, pr_number, summary)
        
        logger.info(f"Posted review for PR #{pr_number} from {repo_name}")
        
        # Notify in Slack
        try:
            slack_app = get_slack_app()
            if slack_app:
                slack_app.client.chat_postMessage(
                    channel=os.environ.get("SLACK_NOTIFICATION_CHANNEL", "general"),
                    text=f"I've reviewed PR #{pr_number} from {repo_name}: {pr_title}\n{pr_url}"
                )
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error analyzing PR #{pr_number} from {repo_name}: {str(e)}")
        raise

def get_slack_app():
    """
    Get the Slack app from the FastAPI app state.
    
    Returns:
        The Slack app, or None if not available
    """
    try:
        from fastapi import FastAPI
        import inspect
        
        # Get the current FastAPI app
        for frame_info in inspect.stack():
            frame = frame_info.frame
            if 'app' in frame.f_locals and isinstance(frame.f_locals['app'], FastAPI):
                fastapi_app = frame.f_locals['app']
                if hasattr(fastapi_app.state, 'slack_app'):
                    return fastapi_app.state.slack_app
    except Exception as e:
        logger.error(f"Error getting Slack app: {str(e)}")
    
    return None
