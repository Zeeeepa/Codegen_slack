"""
Codegen agent for bolt-chat.

This agent integrates with the Codegen library to provide code analysis,
generation, and editing capabilities.
"""

import logging
import os
import sys
from typing import Dict, Any, Optional, List
import importlib.util

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CodegenAgent(BaseAgent):
    """
    Agent for interacting with codebases using Codegen.
    
    This agent provides code analysis, generation, search, and editing capabilities
    through the Codegen library.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new Codegen agent.
        
        Args:
            config: Optional configuration parameters for the agent
        """
        super().__init__(
            name="Codegen Agent",
            description="Analyzes and modifies codebases using Codegen",
            config=config or {}
        )
        
        # Check if codegen is installed
        self.codegen_available = self._check_codegen_available()
        if not self.codegen_available:
            logger.warning("Codegen library not found. Some functionality will be limited.")
        
        # Initialize state
        self.state = {
            "current_codebase": None,
            "current_repo": None,
            "agent_instance": None
        }
    
    def _check_codegen_available(self) -> bool:
        """
        Check if the Codegen library is available.
        
        Returns:
            True if Codegen is available, False otherwise
        """
        try:
            spec = importlib.util.find_spec("codegen")
            return spec is not None
        except ImportError:
            return False
    
    async def initialize(self) -> None:
        """
        Initialize the Codegen agent.
        
        This method is called when the agent is first created or reset.
        """
        await super().initialize()
        
        if not self.codegen_available:
            logger.warning("Codegen library not available. Agent functionality will be limited.")
            return
        
        try:
            # Import Codegen components
            from codegen import CodegenApp, CodeAgent, Codebase
            
            # Initialize default repo if specified in config
            default_repo = self.config.get("default_repo")
            if default_repo:
                self._initialize_codebase(default_repo)
        except Exception as e:
            logger.exception(f"Error initializing Codegen agent: {e}")
    
    def _initialize_codebase(self, repo_name: str) -> bool:
        """
        Initialize a codebase for the specified repository.
        
        Args:
            repo_name: The repository name in the format "owner/repo"
            
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.codegen_available:
            return False
        
        try:
            from codegen import CodegenApp, Codebase
            
            # Create a CodegenApp instance
            app_name = f"bolt_codegen_{repo_name.replace('/', '_')}"
            cg_app = CodegenApp(name=app_name, repo=repo_name)
            
            # Parse the repository
            cg_app.parse_repo()
            
            # Get the codebase
            codebase = cg_app.get_codebase()
            
            # Update state
            self.state["current_codebase"] = codebase
            self.state["current_repo"] = repo_name
            self.state["app_instance"] = cg_app
            
            logger.info(f"Initialized codebase for repository: {repo_name}")
            return True
        except Exception as e:
            logger.exception(f"Error initializing codebase for {repo_name}: {e}")
            return False
    
    def _initialize_agent(self) -> bool:
        """
        Initialize a CodeAgent for the current codebase.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.codegen_available or not self.state["current_codebase"]:
            return False
        
        try:
            from codegen import CodeAgent
            
            # Get model configuration
            model_provider = self.config.get("model_provider", "anthropic")
            model_name = self.config.get("model_name", "claude-3-7-sonnet-latest")
            
            # Create a CodeAgent instance
            agent = CodeAgent(
                codebase=self.state["current_codebase"],
                model_provider=model_provider,
                model_name=model_name
            )
            
            # Update state
            self.state["agent_instance"] = agent
            
            logger.info(f"Initialized CodeAgent with {model_provider}/{model_name}")
            return True
        except Exception as e:
            logger.exception(f"Error initializing CodeAgent: {e}")
            return False
    
    async def process(self, 
                     input_data: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process input data and return a result.
        
        Args:
            input_data: The input data to process
            context: Optional context information
            
        Returns:
            A dictionary containing the processing result
        """
        if not self.codegen_available:
            return {
                "success": False,
                "error": "Codegen library not available",
                "message": "The Codegen library is not installed or not available in the current environment."
            }
        
        # Get the action from input data
        action = input_data.get("action", "analyze")
        
        # Process based on action
        if action == "set_repo":
            return await self._handle_set_repo(input_data, context)
        elif action == "analyze":
            return await self._handle_analyze(input_data, context)
        elif action == "search":
            return await self._handle_search(input_data, context)
        elif action == "generate":
            return await self._handle_generate(input_data, context)
        elif action == "edit":
            return await self._handle_edit(input_data, context)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "message": f"The action '{action}' is not supported by the Codegen agent."
            }
    
    async def _handle_set_repo(self, 
                              input_data: Dict[str, Any], 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle the set_repo action.
        
        Args:
            input_data: The input data containing the repository name
            context: Optional context information
            
        Returns:
            A dictionary containing the result
        """
        repo_name = input_data.get("repo")
        if not repo_name:
            return {
                "success": False,
                "error": "Missing repository name",
                "message": "Please provide a repository name in the format 'owner/repo'."
            }
        
        # Initialize the codebase
        success = self._initialize_codebase(repo_name)
        if not success:
            return {
                "success": False,
                "error": f"Failed to initialize codebase for {repo_name}",
                "message": f"Could not initialize the codebase for repository {repo_name}."
            }
        
        # Initialize the agent
        success = self._initialize_agent()
        if not success:
            return {
                "success": False,
                "error": f"Failed to initialize agent for {repo_name}",
                "message": f"Could not initialize the CodeAgent for repository {repo_name}."
            }
        
        return {
            "success": True,
            "repo": repo_name,
            "message": f"Successfully initialized codebase and agent for repository {repo_name}."
        }
    
    async def _handle_analyze(self, 
                             input_data: Dict[str, Any], 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle the analyze action.
        
        Args:
            input_data: The input data containing the query
            context: Optional context information
            
        Returns:
            A dictionary containing the result
        """
        # Check if agent is initialized
        if not self.state["agent_instance"]:
            # Try to initialize with default repo
            default_repo = self.config.get("default_repo")
            if default_repo:
                success = self._initialize_codebase(default_repo)
                if success:
                    success = self._initialize_agent()
            
            if not self.state["agent_instance"]:
                return {
                    "success": False,
                    "error": "Agent not initialized",
                    "message": "Please set a repository first using the set_repo action."
                }
        
        # Get the query
        query = input_data.get("query")
        if not query:
            return {
                "success": False,
                "error": "Missing query",
                "message": "Please provide a query for analysis."
            }
        
        try:
            # Run the agent
            agent = self.state["agent_instance"]
            response = agent.run(query)
            
            return {
                "success": True,
                "query": query,
                "response": response,
                "repo": self.state["current_repo"]
            }
        except Exception as e:
            logger.exception(f"Error running CodeAgent: {e}")
            return {
                "success": False,
                "error": f"Error running CodeAgent: {str(e)}",
                "message": f"An error occurred while analyzing the codebase: {str(e)}"
            }
    
    async def _handle_search(self, 
                            input_data: Dict[str, Any], 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle the search action.
        
        Args:
            input_data: The input data containing the search query
            context: Optional context information
            
        Returns:
            A dictionary containing the result
        """
        # Check if codebase is initialized
        if not self.state["current_codebase"]:
            return {
                "success": False,
                "error": "Codebase not initialized",
                "message": "Please set a repository first using the set_repo action."
            }
        
        # Get the search query
        query = input_data.get("query")
        if not query:
            return {
                "success": False,
                "error": "Missing search query",
                "message": "Please provide a search query."
            }
        
        try:
            # Get the codebase
            codebase = self.state["current_codebase"]
            
            # Search the codebase
            search_results = codebase.search(query)
            
            # Format the results
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "file": result.file.path,
                    "line": result.line,
                    "content": result.content
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "repo": self.state["current_repo"]
            }
        except Exception as e:
            logger.exception(f"Error searching codebase: {e}")
            return {
                "success": False,
                "error": f"Error searching codebase: {str(e)}",
                "message": f"An error occurred while searching the codebase: {str(e)}"
            }
    
    async def _handle_generate(self, 
                              input_data: Dict[str, Any], 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle the generate action.
        
        Args:
            input_data: The input data containing the generation prompt
            context: Optional context information
            
        Returns:
            A dictionary containing the result
        """
        # Check if agent is initialized
        if not self.state["agent_instance"]:
            return {
                "success": False,
                "error": "Agent not initialized",
                "message": "Please set a repository first using the set_repo action."
            }
        
        # Get the prompt
        prompt = input_data.get("prompt")
        if not prompt:
            return {
                "success": False,
                "error": "Missing generation prompt",
                "message": "Please provide a prompt for code generation."
            }
        
        try:
            # Run the agent
            agent = self.state["agent_instance"]
            response = agent.run(f"Generate code: {prompt}")
            
            return {
                "success": True,
                "prompt": prompt,
                "response": response,
                "repo": self.state["current_repo"]
            }
        except Exception as e:
            logger.exception(f"Error generating code: {e}")
            return {
                "success": False,
                "error": f"Error generating code: {str(e)}",
                "message": f"An error occurred while generating code: {str(e)}"
            }
    
    async def _handle_edit(self, 
                          input_data: Dict[str, Any], 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle the edit action.
        
        Args:
            input_data: The input data containing the edit instructions
            context: Optional context information
            
        Returns:
            A dictionary containing the result
        """
        # Check if agent is initialized
        if not self.state["agent_instance"]:
            return {
                "success": False,
                "error": "Agent not initialized",
                "message": "Please set a repository first using the set_repo action."
            }
        
        # Get the edit instructions
        instructions = input_data.get("instructions")
        if not instructions:
            return {
                "success": False,
                "error": "Missing edit instructions",
                "message": "Please provide instructions for code editing."
            }
        
        # Get the file path
        file_path = input_data.get("file_path")
        
        try:
            # Run the agent
            agent = self.state["agent_instance"]
            
            # Construct the prompt based on whether a file path is provided
            if file_path:
                prompt = f"Edit file {file_path} with these instructions: {instructions}"
            else:
                prompt = f"Edit code with these instructions: {instructions}"
            
            response = agent.run(prompt)
            
            return {
                "success": True,
                "instructions": instructions,
                "file_path": file_path,
                "response": response,
                "repo": self.state["current_repo"]
            }
        except Exception as e:
            logger.exception(f"Error editing code: {e}")
            return {
                "success": False,
                "error": f"Error editing code: {str(e)}",
                "message": f"An error occurred while editing code: {str(e)}"
            }
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities supported by this agent.
        
        Returns:
            A list of capability names
        """
        if not self.codegen_available:
            return ["limited_functionality"]
        
        return [
            "code_analysis",
            "code_search",
            "code_generation",
            "code_editing",
            "repository_management"
        ]