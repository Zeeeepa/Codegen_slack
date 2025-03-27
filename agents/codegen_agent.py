"""
Codegen agent implementation for code analysis, generation, and editing.
"""
import logging
import os
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