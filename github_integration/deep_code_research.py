"""
Deep code research module for PR Review Agent.

This module provides functionality to perform deep code research on repositories
using Codegen's tools and capabilities.
"""

import os
import logging
import tempfile
from typing import Dict, List, Any, Optional, Tuple

from codegen import Codebase
from codegen.extensions.langchain.agent import create_agent_with_tools
from codegen.extensions.langchain.tools import (
    ViewFileTool,
    ListDirectoryTool,
    RipGrepTool,
    SemanticSearchTool,
    RevealSymbolTool,
)
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)

RESEARCH_AGENT_PROMPT = """You are a code research expert assisting with pull request reviews. Your goal is to:
1. Understand the changes in the PR and their context within the broader codebase
2. Identify potential issues, bugs, or improvements in the PR
3. Suggest better approaches or optimizations based on the codebase's patterns and best practices
4. Explain how the changes impact the rest of the codebase

When analyzing code, consider:
- The purpose and functionality of each component
- How different parts interact
- Key patterns and design decisions
- Potential areas for improvement
- Security implications
- Performance considerations
- Maintainability and readability

Break down complex concepts into understandable pieces and provide specific, actionable feedback."""


class DeepCodeResearcher:
    """
    Class for performing deep code research on repositories.
    """

    def __init__(self, repo_name: str, pr_number: int):
        """
        Initialize the deep code researcher.
        
        Args:
            repo_name: The repository name (e.g., "owner/repo")
            pr_number: The PR number
        """
        self.repo_name = repo_name
        self.pr_number = pr_number
        self.codebase = None
        self.agent = None
        self.temp_dir = None
        
    def initialize(self) -> bool:
        """
        Initialize the codebase and agent.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Create a temporary directory for the cloned repository
            self.temp_dir = tempfile.TemporaryDirectory()
            
            logger.info(f"Cloning repository {self.repo_name} for deep code research")
            
            # Clone the repository
            self.codebase = Codebase.from_repo(
                self.repo_name,
                tmp_dir=self.temp_dir.name
            )
            
            # Create research tools
            tools = [
                ViewFileTool(self.codebase),
                ListDirectoryTool(self.codebase),
                RipGrepTool(self.codebase),
                SemanticSearchTool(self.codebase),
                RevealSymbolTool(self.codebase),
            ]
            
            # Initialize agent with research tools
            self.agent = create_agent_with_tools(
                codebase=self.codebase,
                tools=tools,
                system_message=SystemMessage(content=RESEARCH_AGENT_PROMPT)
            )
            
            logger.info(f"Deep code research agent initialized for {self.repo_name} PR #{self.pr_number}")
            return True
        except Exception as e:
            logger.error(f"Error initializing deep code research: {str(e)}")
            self.cleanup()
            return False
    
    def cleanup(self):
        """
        Clean up resources.
        """
        if self.temp_dir:
            try:
                self.temp_dir.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up temporary directory: {str(e)}")
    
    def research_pr_changes(self, changed_files: List[Dict[str, Any]], pr_description: str) -> str:
        """
        Research the PR changes and provide insights.
        
        Args:
            changed_files: List of changed files with their paths and status
            pr_description: The PR description
            
        Returns:
            str: Research findings and insights
        """
        if not self.agent:
            logger.error("Agent not initialized")
            return "Error: Deep code research agent not initialized"
        
        try:
            # Create a prompt for the agent
            file_list = "\n".join([f"- {f['filename']} ({f['status']})" for f in changed_files])
            
            prompt = f"""
            I'm reviewing a pull request (PR #{self.pr_number}) in the repository {self.repo_name}.
            
            PR Description:
            {pr_description}
            
            Changed files:
            {file_list}
            
            Please help me understand:
            1. What is the purpose of these changes?
            2. How do these changes fit into the broader codebase?
            3. Are there any potential issues or improvements in these changes?
            4. Are there any patterns or best practices in the codebase that should be followed?
            5. What are the potential impacts of these changes on the rest of the codebase?
            
            Please provide specific, actionable feedback that I can use to improve the PR.
            """
            
            # Invoke the agent
            result = self.agent.invoke({"input": prompt})
            
            # Extract the response
            response = result["messages"][-1].content
            
            logger.info(f"Deep code research completed for {self.repo_name} PR #{self.pr_number}")
            
            return response
        except Exception as e:
            logger.error(f"Error during deep code research: {str(e)}")
            return f"Error during deep code research: {str(e)}"
        finally:
            self.cleanup()
    
    def answer_question(self, question: str, context: Optional[str] = None) -> str:
        """
        Answer a specific question about the codebase.
        
        Args:
            question: The question to answer
            context: Optional additional context
            
        Returns:
            str: The answer to the question
        """
        if not self.agent:
            logger.error("Agent not initialized")
            return "Error: Deep code research agent not initialized"
        
        try:
            # Create a prompt for the agent
            prompt = f"""
            I'm reviewing a pull request (PR #{self.pr_number}) in the repository {self.repo_name}.
            
            I have a specific question about the codebase:
            {question}
            """
            
            if context:
                prompt += f"""
                Additional context:
                {context}
                """
            
            # Invoke the agent
            result = self.agent.invoke({"input": prompt})
            
            # Extract the response
            response = result["messages"][-1].content
            
            logger.info(f"Question answered for {self.repo_name} PR #{self.pr_number}")
            
            return response
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return f"Error answering question: {str(e)}"