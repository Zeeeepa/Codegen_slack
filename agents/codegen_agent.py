"""
Codegen agent implementation for code analysis, generation, and editing.
"""
import logging
import os
import time
from typing import Optional, Dict, Any

from codegen import CodeAgent, CodegenApp
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CodegenAgent(BaseAgent):
    """
    Agent for code analysis, generation, and editing using Codegen.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the Codegen agent.
        
        Args:
            **kwargs: Additional arguments for the agent
        """
        super().__init__(**kwargs)
        self.repo = kwargs.get("repo", os.environ.get("CODEGEN_DEFAULT_REPO", "Zeeeepa/bolt-chat"))
        self.cg_app = CodegenApp(name="bolt-codegen", repo=self.repo)
        logger.info(f"Initialized CodegenAgent with repo: {self.repo}")
        
        # Parse the repository on initialization
        self._ensure_repo_parsed()
    
    def _ensure_repo_parsed(self):
        """
        Ensure the repository is parsed before using it.
        """
        try:
            logger.info(f"Parsing repository: {self.repo}")
            # Get codebase will trigger parsing if not already parsed
            codebase = self.cg_app.get_codebase()
            
            # Check if the repository is parsed
            if not codebase.files:
                logger.info("Repository not parsed yet. Parsing...")
                # Force a parse by checking out the default branch
                codebase.checkout()
                # Wait for parsing to complete
                max_retries = 5
                for i in range(max_retries):
                    time.sleep(2)  # Wait for parsing to complete
                    codebase = self.cg_app.get_codebase()
                    if codebase.files:
                        logger.info(f"Repository parsed successfully. Found {len(codebase.files)} files.")
                        break
                    logger.info(f"Waiting for repository parsing... Attempt {i+1}/{max_retries}")
                
                if not codebase.files:
                    logger.warning("Repository parsing may not have completed. Proceeding anyway.")
            else:
                logger.info(f"Repository already parsed. Found {len(codebase.files)} files.")
        except Exception as e:
            logger.error(f"Error parsing repository: {e}")
            # Continue anyway, as the error will be handled in process_message
    
    def process_message(self, message: str, context: Optional[str] = None) -> str:
        """
        Process a message using the Codegen agent.
        
        Args:
            message: The message to process
            context: Optional context for the message
            
        Returns:
            The response from the Codegen agent
        """
        try:
            logger.info(f"Processing message with CodegenAgent: {message}")
            
            # Get codebase
            codebase = self.cg_app.get_codebase()
            
            # Check if repository is parsed
            if not codebase.files:
                # Try to parse the repository again
                self._ensure_repo_parsed()
                codebase = self.cg_app.get_codebase()
                
                # If still not parsed, return an error message
                if not codebase.files:
                    return "I'm still initializing and parsing the repository. Please try again in a few moments."
            
            # Initialize code agent
            agent = CodeAgent(codebase=codebase)
            
            # Add context if provided
            full_message = message
            if context:
                full_message = f"Context: {context}\n\nMessage: {message}"
            
            # Run the agent with the message
            response = agent.run(full_message)
            
            return response
        except Exception as e:
            logger.error(f"Error processing message with CodegenAgent: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    @classmethod
    def get_description(cls) -> str:
        return "Agent for code analysis, generation, and editing using Codegen."