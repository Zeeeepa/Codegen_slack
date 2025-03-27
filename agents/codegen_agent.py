"""
Codegen agent implementation for code analysis, generation, and editing.
"""
import logging
import os
import time
import threading
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
        self.parsing_status = "not_started"  # Possible values: not_started, in_progress, completed, failed
        self.parsing_error = None
        self.parsing_lock = threading.Lock()
        logger.info(f"Initialized CodegenAgent with repo: {self.repo}")
        
        # Start repository parsing in a background thread
        self._start_repo_parsing()
    
    def _start_repo_parsing(self):
        """
        Start repository parsing in a background thread.
        """
        def parse_repo():
            with self.parsing_lock:
                self.parsing_status = "in_progress"
                try:
                    logger.info(f"Starting repository parsing for {self.repo}")
                    # Get codebase will trigger parsing if not already parsed
                    codebase = self.cg_app.get_codebase()
                    
                    # Check if the repository is already parsed
                    if codebase.files:
                        logger.info(f"Repository already parsed. Found {len(codebase.files)} files.")
                        self.parsing_status = "completed"
                        return
                    
                    # Force a parse by checking out the default branch
                    logger.info("Repository not parsed yet. Forcing parse...")
                    codebase.checkout()
                    
                    # Wait for parsing to complete with increasing backoff
                    max_retries = 10
                    base_wait_time = 2
                    for i in range(max_retries):
                        wait_time = base_wait_time * (i + 1)
                        logger.info(f"Waiting for repository parsing... Attempt {i+1}/{max_retries} (waiting {wait_time}s)")
                        time.sleep(wait_time)
                        
                        # Check if parsing is complete
                        codebase = self.cg_app.get_codebase()
                        if codebase.files:
                            logger.info(f"Repository parsed successfully. Found {len(codebase.files)} files.")
                            self.parsing_status = "completed"
                            return
                    
                    # If we get here, parsing didn't complete within the retry limit
                    logger.warning("Repository parsing timed out. Setting status to failed.")
                    self.parsing_status = "failed"
                    self.parsing_error = "Parsing timed out after multiple attempts"
                except Exception as e:
                    logger.error(f"Error parsing repository: {e}")
                    self.parsing_status = "failed"
                    self.parsing_error = str(e)
        
        # Start parsing in a background thread
        parsing_thread = threading.Thread(target=parse_repo)
        parsing_thread.daemon = True
        parsing_thread.start()
        logger.info("Started repository parsing in background thread")
    
    def _retry_repo_parsing(self):
        """
        Retry repository parsing if it failed.
        """
        with self.parsing_lock:
            if self.parsing_status == "failed":
                logger.info("Retrying repository parsing")
                self.parsing_status = "not_started"
                self.parsing_error = None
                self._start_repo_parsing()
                return True
            return False
    
    def get_parsing_status(self):
        """
        Get the current parsing status.
        
        Returns:
            A dictionary with the current parsing status
        """
        with self.parsing_lock:
            return {
                "status": self.parsing_status,
                "error": self.parsing_error,
                "repo": self.repo
            }
    
    def process_message(self, message: str, context: Optional[str] = None) -> str:
        """
        Process a message using the Codegen agent.
        
        Args:
            message: The message to process
            context: Optional context for the message
            
        Returns:
            The response from the Codegen agent
        """
        logger.info(f"Processing message with CodegenAgent: {message}")
        
        # Check parsing status
        with self.parsing_lock:
            current_status = self.parsing_status
            current_error = self.parsing_error
        
        # Handle different parsing statuses
        if current_status == "not_started":
            # Start parsing if not already started
            self._start_repo_parsing()
            return (
                f"I'm initializing and starting to parse the repository `{self.repo}`. "
                f"This may take a few minutes for larger repositories. "
                f"Please try again in a moment."
            )
        
        elif current_status == "in_progress":
            # Parsing is still in progress
            return (
                f"I'm still parsing the repository `{self.repo}`. "
                f"This process can take a few minutes for larger repositories. "
                f"Please try again in a moment."
            )
        
        elif current_status == "failed":
            # Parsing failed, try to retry
            if "retry" in message.lower() or "parse again" in message.lower():
                if self._retry_repo_parsing():
                    return (
                        f"I'm retrying the repository parsing for `{self.repo}`. "
                        f"Please try again in a moment."
                    )
            
            # Return error message with instructions to retry
            return (
                f"Repository parsing failed with error: {current_error}\n\n"
                f"This could be due to network issues, repository access problems, or temporary Codegen service issues. "
                f"You can ask me to 'retry parsing' to attempt again."
            )
        
        # If we get here, parsing should be completed
        try:
            # Get codebase
            codebase = self.cg_app.get_codebase()
            
            # Double-check that we have files
            if not codebase.files:
                logger.warning("Parsing status is 'completed' but no files found. Setting status to failed.")
                with self.parsing_lock:
                    self.parsing_status = "failed"
                    self.parsing_error = "Repository parsed but no files found"
                
                return (
                    f"Repository parsing completed but no files were found in `{self.repo}`. "
                    f"This could indicate an issue with repository access or configuration. "
                    f"You can ask me to 'retry parsing' to attempt again."
                )
            
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
            
            # Check if this is a parsing error
            if "Repository has not been parsed" in str(e):
                with self.parsing_lock:
                    self.parsing_status = "failed"
                    self.parsing_error = str(e)
                
                return (
                    f"I encountered an error: Repository has not been parsed.\n\n"
                    f"This usually means the repository parsing is still in progress or failed. "
                    f"Please wait a few minutes and try again, or ask me to 'retry parsing'."
                )
            
            return f"I encountered an error while processing your request: {str(e)}"
    
    @classmethod
    def get_description(cls) -> str:
        return "Agent for code analysis, generation, and editing using Codegen."