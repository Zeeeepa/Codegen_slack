"""
Command to ask questions about a PR's code.
"""

import logging
import re
from slack_bolt import App, Ack, Say
from github_integration.pr_analyzer import get_pr_details
from github_integration.github_api import get_pr_files
from github_integration.deep_code_research import DeepCodeResearcher

logger = logging.getLogger(__name__)

def ask_pr_question_command(ack, command, say):
    """
    Handle the /ask-pr-question command.
    
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
        say("Please provide a PR reference and a question, e.g., 'owner/repo#123 How does this code handle error cases?'")
        return
    
    # Try to extract repo, PR number, and question from the text
    repo_name, pr_number, question = parse_pr_question(text)
    
    if not repo_name or not pr_number or not question:
        say("Invalid format. Please use: `/ask-pr-question owner/repo#123 Your question here`")
        return
    
    # Acknowledge the command
    say(f"Analyzing PR #{pr_number} in {repo_name} to answer your question. This may take a minute...")
    
    try:
        # Initialize the deep code researcher
        researcher = DeepCodeResearcher(repo_name, pr_number)
        if not researcher.initialize():
            say(f"Failed to initialize code research for PR #{pr_number} in {repo_name}. Please try again later.")
            return
        
        # Get PR details for context
        pr_details = get_pr_details(repo_name, pr_number)
        pr_title = pr_details.get("title", "")
        pr_description = pr_details.get("body", "")
        pr_url = pr_details.get("html_url", "")
        
        # Get PR files for context
        pr_files = get_pr_files(repo_name, pr_number)
        
        # Create context for the question
        context = f"""
PR Title: {pr_title}
PR Description: {pr_description}
Changed files: {', '.join([f['filename'] for f in pr_files])}
        """
        
        # Get the answer
        answer = researcher.answer_question(question, context)
        
        # Send the answer
        say(
            f"*Question about PR #{pr_number} in {repo_name}*\n"
            f"*Question:* {question}\n\n"
            f"*Answer:*\n{answer}\n\n"
            f"<{pr_url}|View PR on GitHub>"
        )
    except Exception as e:
        logger.error(f"Error answering question about PR: {str(e)}")
        say(f"Error answering question: {str(e)}")

def parse_pr_question(text):
    """
    Parse a PR reference and question from text.
    
    Args:
        text: The text to parse
    
    Returns:
        tuple: (repo_name, pr_number, question) or (None, None, None) if parsing fails
    """
    # Try to match a GitHub PR URL with question
    url_pattern = r"https?://github\.com/([^/]+/[^/]+)/pull/(\d+)\s+(.+)"
    url_match = re.search(url_pattern, text)
    if url_match:
        return url_match.group(1), int(url_match.group(2)), url_match.group(3).strip()
    
    # Try to match a repo#pr format with question
    repo_pr_pattern = r"([^/]+/[^#]+)#(\d+)\s+(.+)"
    repo_pr_match = re.search(repo_pr_pattern, text)
    if repo_pr_match:
        return repo_pr_match.group(1), int(repo_pr_match.group(2)), repo_pr_match.group(3).strip()
    
    return None, None, None

def register(app: App):
    """
    Register the ask-pr-question command.
    
    Args:
        app: The Bolt app
    """
    app.command("/ask-pr-question")(ask_pr_question_command)