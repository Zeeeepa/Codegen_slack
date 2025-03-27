"""
GitHub API integration for PR review agent.
"""

import os
import logging
import requests
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

def get_github_token() -> str:
    """
    Get the GitHub token from environment variables.
    
    Returns:
        str: The GitHub token
    
    Raises:
        ValueError: If the GitHub token is not set
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")
    return token

def get_github_headers() -> Dict[str, str]:
    """
    Get the headers for GitHub API requests.
    
    Returns:
        Dict[str, str]: The headers for GitHub API requests
    """
    return {
        "Authorization": f"token {get_github_token()}",
        "Accept": "application/vnd.github.v3+json",
    }

def get_pr_details(repo_name: str, pr_number: int) -> Dict[str, Any]:
    """
    Get the details of a pull request.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
        pr_number: The number of the pull request
    
    Returns:
        Dict[str, Any]: The pull request details
    
    Raises:
        Exception: If the request fails
    """
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
    response = requests.get(url, headers=get_github_headers())
    
    if response.status_code != 200:
        raise Exception(f"Failed to get PR details: {response.status_code} {response.text}")
    
    return response.json()

def get_pr_files(repo_name: str, pr_number: int) -> List[Dict[str, Any]]:
    """
    Get the files changed in a pull request.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
        pr_number: The number of the pull request
    
    Returns:
        List[Dict[str, Any]]: The files changed in the pull request
    
    Raises:
        Exception: If the request fails
    """
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
    response = requests.get(url, headers=get_github_headers())
    
    if response.status_code != 200:
        raise Exception(f"Failed to get PR files: {response.status_code} {response.text}")
    
    return response.json()

def post_pr_comment(repo_name: str, pr_number: int, comment: str) -> Dict[str, Any]:
    """
    Post a comment on a pull request.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
        pr_number: The number of the pull request
        comment: The comment to post
    
    Returns:
        Dict[str, Any]: The response from the GitHub API
    
    Raises:
        Exception: If the request fails
    """
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    data = {"body": comment}
    
    response = requests.post(url, headers=get_github_headers(), json=data)
    
    if response.status_code != 201:
        raise Exception(f"Failed to post PR comment: {response.status_code} {response.text}")
    
    return response.json()

def post_pr_review_comment(
    repo_name: str, 
    pr_number: int, 
    commit_id: str, 
    path: str, 
    position: int, 
    body: str
) -> Dict[str, Any]:
    """
    Post a review comment on a specific line in a pull request.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
        pr_number: The number of the pull request
        commit_id: The SHA of the commit to comment on
        path: The path of the file to comment on
        position: The position in the diff to comment on
        body: The comment to post
    
    Returns:
        Dict[str, Any]: The response from the GitHub API
    
    Raises:
        Exception: If the request fails
    """
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/comments"
    data = {
        "commit_id": commit_id,
        "path": path,
        "position": position,
        "body": body,
    }
    
    response = requests.post(url, headers=get_github_headers(), json=data)
    
    if response.status_code != 201:
        raise Exception(f"Failed to post PR review comment: {response.status_code} {response.text}")
    
    return response.json()