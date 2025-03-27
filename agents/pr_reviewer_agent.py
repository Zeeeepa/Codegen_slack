"""
PR Reviewer agent for analyzing GitHub pull requests.
"""

import logging
import os
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from github_integration.pr_analyzer import analyze_pr

logger = logging.getLogger(__name__)

class PRReviewerAgent(BaseAgent):
    """
    Agent for reviewing GitHub pull requests.
    
    This agent analyzes pull requests and provides feedback on code quality,
    best practices, and potential issues.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new PR reviewer agent.
        
        Args:
            config: Optional configuration parameters
        """
        super().__init__(
            name="PR Reviewer",
            description="Reviews GitHub pull requests and provides feedback",
            config=config
        )
    
    async def process(self, 
                     input_data: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a PR review request.
        
        Args:
            input_data: The input data containing PR information
            context: Optional context information
            
        Returns:
            A dictionary containing the review result
        """
        logger.info("Processing PR review request")
        
        # Extract PR information from input data
        pr_url = input_data.get("pr_url")
        repo_name = input_data.get("repo_name")
        pr_number = input_data.get("pr_number")
        pr_title = input_data.get("pr_title")
        
        # Validate input
        if not pr_url and (not repo_name or not pr_number):
            raise ValueError("Either pr_url or both repo_name and pr_number must be provided")
        
        # Parse PR URL if provided
        if pr_url and not (repo_name and pr_number):
            repo_name, pr_number = self._parse_pr_url(pr_url)
        
        # Get PR title if not provided
        if not pr_title:
            pr_title = self._get_pr_title(repo_name, pr_number)
        
        # Analyze the PR
        try:
            review_result = await self._analyze_pr(repo_name, pr_number, pr_title, pr_url)
            
            return {
                "success": True,
                "review": review_result,
                "pr_url": pr_url or f"https://github.com/{repo_name}/pull/{pr_number}",
                "repo_name": repo_name,
                "pr_number": pr_number,
                "pr_title": pr_title
            }
        except Exception as e:
            logger.error(f"Error analyzing PR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "pr_url": pr_url or f"https://github.com/{repo_name}/pull/{pr_number}",
                "repo_name": repo_name,
                "pr_number": pr_number,
                "pr_title": pr_title
            }
    
    def _parse_pr_url(self, pr_url: str) -> tuple:
        """
        Parse a PR URL to extract repository name and PR number.
        
        Args:
            pr_url: The PR URL
            
        Returns:
            A tuple of (repo_name, pr_number)
        """
        # Handle different URL formats
        if "github.com" in pr_url:
            # Format: https://github.com/owner/repo/pull/123
            parts = pr_url.split("github.com/")[1].split("/pull/")
            repo_name = parts[0]
            pr_number = int(parts[1].split("/")[0])
        elif "#" in pr_url:
            # Format: owner/repo#123
            parts = pr_url.split("#")
            repo_name = parts[0]
            pr_number = int(parts[1])
        else:
            raise ValueError(f"Invalid PR URL format: {pr_url}")
        
        return repo_name, pr_number
    
    def _get_pr_title(self, repo_name: str, pr_number: int) -> str:
        """
        Get the title of a PR.
        
        Args:
            repo_name: The repository name
            pr_number: The PR number
            
        Returns:
            The PR title
        """
        # This would typically call the GitHub API to get PR details
        # For now, return a placeholder
        return f"PR #{pr_number} in {repo_name}"
    
    async def _analyze_pr(self, repo_name: str, pr_number: int, pr_title: str, pr_url: str) -> Dict[str, Any]:
        """
        Analyze a PR and generate a review.
        
        Args:
            repo_name: The repository name
            pr_number: The PR number
            pr_title: The PR title
            pr_url: The PR URL
            
        Returns:
            The review result
        """
        # Call the existing PR analyzer
        analyze_pr(repo_name, pr_number, pr_title, pr_url)
        
        # Return a placeholder result
        return {
            "summary": f"Analyzed PR #{pr_number} in {repo_name}",
            "suggestions": [
                "Suggestion 1",
                "Suggestion 2",
                "Suggestion 3"
            ],
            "files_analyzed": 0
        }
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities supported by this agent.
        
        Returns:
            A list of capability names
        """
        return ["pr_review", "code_analysis"]