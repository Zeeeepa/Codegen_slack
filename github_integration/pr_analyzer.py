"""
PR analyzer for GitHub PR review agent.
"""

import os
import logging
import base64
from typing import Dict, List, Any, Optional, Tuple
import anthropic
import openai
from github_integration.github_api import get_pr_details, get_pr_files

logger = logging.getLogger(__name__)

def get_file_content(repo_name: str, file_path: str, ref: str) -> str:
    """
    Get the content of a file from GitHub.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
        file_path: The path of the file
        ref: The reference (branch, commit) to get the file from
    
    Returns:
        str: The content of the file
    
    Raises:
        Exception: If the request fails
    """
    import requests
    from github_integration.github_api import get_github_headers
    
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}?ref={ref}"
    response = requests.get(url, headers=get_github_headers())
    
    if response.status_code != 200:
        raise Exception(f"Failed to get file content: {response.status_code} {response.text}")
    
    content = response.json().get("content", "")
    if content:
        return base64.b64decode(content).decode("utf-8")
    return ""

def analyze_pull_request(repo_name: str, pr_number: int) -> str:
    """
    Analyze a pull request and generate improvement suggestions.
    
    Args:
        repo_name: The name of the repository (e.g., "owner/repo")
        pr_number: The number of the pull request
    
    Returns:
        str: The analysis result with improvement suggestions
    """
    logger.info(f"Analyzing PR #{pr_number} in {repo_name}")
    
    # Get PR details
    pr_details = get_pr_details(repo_name, pr_number)
    pr_title = pr_details.get("title", "")
    pr_body = pr_details.get("body", "")
    pr_head_sha = pr_details.get("head", {}).get("sha", "")
    
    # Get files changed in the PR
    files = get_pr_files(repo_name, pr_number)
    
    # Prepare analysis context
    analysis_context = {
        "pr_title": pr_title,
        "pr_body": pr_body,
        "files": []
    }
    
    # Process each file
    for file in files:
        file_path = file.get("filename", "")
        file_status = file.get("status", "")
        file_changes = file.get("patch", "")
        
        # Skip files that are too large or binary
        if not file_changes and file_status != "removed":
            logger.info(f"Skipping file {file_path} (no diff available)")
            continue
        
        # Get file content for context if needed
        file_content = ""
        if file_status != "removed":
            try:
                file_content = get_file_content(repo_name, file_path, pr_head_sha)
            except Exception as e:
                logger.warning(f"Failed to get content for {file_path}: {str(e)}")
        
        analysis_context["files"].append({
            "path": file_path,
            "status": file_status,
            "changes": file_changes,
            "content": file_content
        })
    
    # Generate analysis using AI
    analysis_result = generate_analysis(analysis_context)
    
    return analysis_result

def generate_analysis(context: Dict[str, Any]) -> str:
    """
    Generate analysis for a PR using AI.
    
    Args:
        context: The context for analysis
    
    Returns:
        str: The analysis result
    """
    # Determine which AI provider to use
    ai_provider = os.environ.get("PR_REVIEW_AI_PROVIDER", "openai").lower()
    
    if ai_provider == "anthropic":
        return generate_analysis_anthropic(context)
    else:
        return generate_analysis_openai(context)

def generate_analysis_openai(context: Dict[str, Any]) -> str:
    """
    Generate analysis using OpenAI.
    
    Args:
        context: The context for analysis
    
    Returns:
        str: The analysis result
    """
    # Prepare the prompt
    files_text = ""
    for file in context["files"]:
        files_text += f"File: {file['path']} ({file['status']})\n"
        files_text += f"Changes:\n```diff\n{file['changes']}\n```\n\n"
        if file['content'] and len(file['content']) < 5000:  # Limit content size
            files_text += f"Full content:\n```\n{file['content']}\n```\n\n"
    
    prompt = f"""
You are an expert code reviewer. Analyze the following pull request and provide constructive feedback and improvement suggestions.

PR Title: {context['pr_title']}
PR Description: {context['pr_body']}

Changed Files:
{files_text}

Please provide a detailed review that includes:
1. Overall assessment of the changes
2. Specific code improvement suggestions
3. Potential bugs or issues
4. Best practices that could be applied
5. Performance considerations
6. Security considerations (if applicable)

Format your response as a GitHub comment with markdown formatting.
"""
    
    # Call OpenAI API
    try:
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=os.environ.get("PR_REVIEW_OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are an expert code reviewer providing constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating analysis with OpenAI: {str(e)}")
        return f"Error generating PR analysis: {str(e)}"

def generate_analysis_anthropic(context: Dict[str, Any]) -> str:
    """
    Generate analysis using Anthropic.
    
    Args:
        context: The context for analysis
    
    Returns:
        str: The analysis result
    """
    # Prepare the prompt
    files_text = ""
    for file in context["files"]:
        files_text += f"File: {file['path']} ({file['status']})\n"
        files_text += f"Changes:\n```diff\n{file['changes']}\n```\n\n"
        if file['content'] and len(file['content']) < 5000:  # Limit content size
            files_text += f"Full content:\n```\n{file['content']}\n```\n\n"
    
    prompt = f"""
You are an expert code reviewer. Analyze the following pull request and provide constructive feedback and improvement suggestions.

PR Title: {context['pr_title']}
PR Description: {context['pr_body']}

Changed Files:
{files_text}

Please provide a detailed review that includes:
1. Overall assessment of the changes
2. Specific code improvement suggestions
3. Potential bugs or issues
4. Best practices that could be applied
5. Performance considerations
6. Security considerations (if applicable)

Format your response as a GitHub comment with markdown formatting.
"""
    
    # Call Anthropic API
    try:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=os.environ.get("PR_REVIEW_ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            max_tokens=4000,
            temperature=0.1,
            system="You are an expert code reviewer providing constructive feedback.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Error generating analysis with Anthropic: {str(e)}")
        return f"Error generating PR analysis: {str(e)}"