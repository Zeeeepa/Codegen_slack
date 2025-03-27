"""
Codegen agent implementation for bolt-chat.
"""

import logging
import os
import json
import requests
from typing import Dict, Any, List, Optional, Union

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CodegenAgent(BaseAgent):
    """
    Agent for integrating with Codegen.
    
    This agent provides access to Codegen's code analysis and generation capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new Codegen agent.
        
        Args:
            config: Optional configuration parameters
        """
        super().__init__(
            name="Codegen Agent",
            description="Agent for code analysis and generation using Codegen",
            config=config
        )
        
        # Set up Codegen API configuration
        self.api_base_url = self.config.get("api_base_url", os.environ.get("CODEGEN_API_URL", "http://localhost:8000"))
        self.api_key = self.config.get("api_key", os.environ.get("CODEGEN_API_KEY"))
        
    async def process(self, 
                     input_data: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a code-related request.
        
        Args:
            input_data: The input data containing code information
            context: Optional context information
            
        Returns:
            A dictionary containing the processing result
        """
        logger.info("Processing code request with Codegen agent")
        
        # Extract request parameters
        action = input_data.get("action", "analyze")
        code = input_data.get("code", "")
        repo = input_data.get("repo", "")
        file_path = input_data.get("file_path", "")
        query = input_data.get("query", "")
        
        # Process based on the requested action
        if action == "analyze":
            return await self._analyze_code(code, repo, file_path)
        elif action == "generate":
            return await self._generate_code(query, repo, file_path)
        elif action == "search":
            return await self._search_code(query, repo)
        elif action == "edit":
            return await self._edit_code(code, input_data.get("edit_instructions", ""), repo, file_path)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
    
    async def _analyze_code(self, code: str, repo: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze code using Codegen.
        
        Args:
            code: The code to analyze
            repo: The repository name
            file_path: The file path
            
        Returns:
            The analysis result
        """
        try:
            # Call Codegen API for code analysis
            response = self._call_codegen_api(
                endpoint="/api/analyze",
                method="POST",
                data={
                    "code": code,
                    "repo": repo,
                    "file_path": file_path
                }
            )
            
            return {
                "success": True,
                "analysis": response,
                "repo": repo,
                "file_path": file_path
            }
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repo": repo,
                "file_path": file_path
            }
    
    async def _generate_code(self, query: str, repo: str, file_path: str) -> Dict[str, Any]:
        """
        Generate code using Codegen.
        
        Args:
            query: The generation query
            repo: The repository name
            file_path: The file path
            
        Returns:
            The generation result
        """
        try:
            # Call Codegen API for code generation
            response = self._call_codegen_api(
                endpoint="/api/generate",
                method="POST",
                data={
                    "query": query,
                    "repo": repo,
                    "file_path": file_path
                }
            )
            
            return {
                "success": True,
                "generated_code": response.get("code", ""),
                "repo": repo,
                "file_path": file_path
            }
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repo": repo,
                "file_path": file_path
            }
    
    async def _search_code(self, query: str, repo: str) -> Dict[str, Any]:
        """
        Search code using Codegen.
        
        Args:
            query: The search query
            repo: The repository name
            
        Returns:
            The search result
        """
        try:
            # Call Codegen API for code search
            response = self._call_codegen_api(
                endpoint="/api/search",
                method="GET",
                params={
                    "query": query,
                    "repo": repo
                }
            )
            
            return {
                "success": True,
                "search_results": response.get("results", []),
                "repo": repo
            }
        except Exception as e:
            logger.error(f"Error searching code: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repo": repo
            }
    
    async def _edit_code(self, code: str, edit_instructions: str, repo: str, file_path: str) -> Dict[str, Any]:
        """
        Edit code using Codegen.
        
        Args:
            code: The code to edit
            edit_instructions: Instructions for editing
            repo: The repository name
            file_path: The file path
            
        Returns:
            The edit result
        """
        try:
            # Call Codegen API for code editing
            response = self._call_codegen_api(
                endpoint="/api/edit",
                method="POST",
                data={
                    "code": code,
                    "instructions": edit_instructions,
                    "repo": repo,
                    "file_path": file_path
                }
            )
            
            return {
                "success": True,
                "edited_code": response.get("code", ""),
                "repo": repo,
                "file_path": file_path
            }
        except Exception as e:
            logger.error(f"Error editing code: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repo": repo,
                "file_path": file_path
            }
    
    def _call_codegen_api(self, 
                         endpoint: str, 
                         method: str = "GET", 
                         params: Optional[Dict[str, Any]] = None,
                         data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call the Codegen API.
        
        Args:
            endpoint: The API endpoint
            method: The HTTP method
            params: Optional query parameters
            data: Optional request data
            
        Returns:
            The API response
        """
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Codegen API: {str(e)}")
            raise
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities supported by this agent.
        
        Returns:
            A list of capability names
        """
        return ["code_analysis", "code_generation", "code_search", "code_editing"]