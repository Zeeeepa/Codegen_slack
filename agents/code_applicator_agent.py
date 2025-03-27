"""
Code Applicator agent for implementing code changes.
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional, Union

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CodeApplicatorAgent(BaseAgent):
    """
    Agent for implementing code changes.
    
    This agent can analyze code, generate implementations, and apply changes
    to codebases based on specifications or requirements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new code applicator agent.
        
        Args:
            config: Optional configuration parameters
        """
        super().__init__(
            name="Code Applicator",
            description="Implements code changes based on specifications",
            config=config
        )
        
        # Initialize code tools based on config
        self.supported_languages = config.get("supported_languages", ["python", "javascript", "typescript"]) if config else ["python", "javascript", "typescript"]
        self.max_file_size = config.get("max_file_size", 10000) if config else 10000
        
        # Initialize state
        self.state = {
            "change_history": [],
            "current_change": None,
            "changes": {}
        }
    
    async def process(self, 
                     input_data: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a code change request.
        
        Args:
            input_data: The input data containing code change parameters
            context: Optional context information
            
        Returns:
            A dictionary containing the code change results
        """
        logger.info("Processing code change request")
        
        # Extract code change parameters
        specification = input_data.get("specification")
        code_context = input_data.get("code_context", {})
        language = input_data.get("language", "python")
        file_paths = input_data.get("file_paths", [])
        
        # Validate input
        if not specification:
            raise ValueError("Code change specification must be provided")
        
        # Update state
        self.state["current_change"] = {
            "specification": specification,
            "language": language,
            "file_paths": file_paths,
            "status": "in_progress"
        }
        
        # Add to change history
        self.state["change_history"].append(specification)
        
        # Implement code change
        try:
            change_result = await self._implement_change(specification, code_context, language, file_paths)
            
            # Update state
            self.state["current_change"]["status"] = "completed"
            self.state["changes"][specification] = change_result
            
            return {
                "success": True,
                "specification": specification,
                "changes": change_result,
                "language": language,
                "files_changed": len(change_result.get("files_changed", [])),
                "summary": change_result.get("summary", "")
            }
        except Exception as e:
            logger.error(f"Error implementing code change: {str(e)}")
            
            # Update state
            self.state["current_change"]["status"] = "failed"
            self.state["current_change"]["error"] = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "specification": specification,
                "language": language
            }
    
    async def _implement_change(self, 
                              specification: str, 
                              code_context: Dict[str, Any], 
                              language: str, 
                              file_paths: List[str]) -> Dict[str, Any]:
        """
        Implement a code change based on the specification.
        
        Args:
            specification: The code change specification
            code_context: Context information about the codebase
            language: The programming language
            file_paths: List of file paths to modify
            
        Returns:
            A dictionary containing the code change results
        """
        # Validate language
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        
        # Analyze code context
        analysis = await self._analyze_code_context(code_context, language)
        
        # Generate code changes
        changes = await self._generate_code_changes(specification, analysis, language, file_paths)
        
        # Apply changes
        applied_changes = await self._apply_changes(changes, file_paths)
        
        # Generate summary
        summary = await self._generate_change_summary(specification, applied_changes)
        
        return {
            "specification": specification,
            "language": language,
            "files_changed": applied_changes,
            "summary": summary
        }
    
    async def _analyze_code_context(self, 
                                  code_context: Dict[str, Any], 
                                  language: str) -> Dict[str, Any]:
        """
        Analyze the code context to understand the codebase.
        
        Args:
            code_context: Context information about the codebase
            language: The programming language
            
        Returns:
            A dictionary containing the analysis results
        """
        # This would typically analyze the code structure, dependencies, etc.
        # For now, return a placeholder analysis
        return {
            "language": language,
            "dependencies": code_context.get("dependencies", []),
            "imports": code_context.get("imports", []),
            "classes": code_context.get("classes", []),
            "functions": code_context.get("functions", []),
            "variables": code_context.get("variables", [])
        }
    
    async def _generate_code_changes(self, 
                                   specification: str, 
                                   analysis: Dict[str, Any], 
                                   language: str, 
                                   file_paths: List[str]) -> Dict[str, Any]:
        """
        Generate code changes based on the specification and analysis.
        
        Args:
            specification: The code change specification
            analysis: The code context analysis
            language: The programming language
            file_paths: List of file paths to modify
            
        Returns:
            A dictionary containing the generated code changes
        """
        # This would typically use an LLM to generate code changes
        # For now, return placeholder changes
        changes = {}
        
        for file_path in file_paths:
            changes[file_path] = {
                "original": f"# Original code for {file_path}",
                "modified": f"# Modified code for {file_path} based on: {specification}",
                "diff": f"--- {file_path}\n+++ {file_path}\n@@ -1,1 +1,1 @@\n-# Original code\n+# Modified code"
            }
        
        return {
            "changes": changes,
            "new_files": [],
            "deleted_files": []
        }
    
    async def _apply_changes(self, 
                           changes: Dict[str, Any], 
                           file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Apply the generated code changes to the files.
        
        Args:
            changes: The generated code changes
            file_paths: List of file paths to modify
            
        Returns:
            A list of applied changes
        """
        # This would typically write the changes to the files
        # For now, return placeholder applied changes
        applied_changes = []
        
        for file_path in file_paths:
            if file_path in changes.get("changes", {}):
                applied_changes.append({
                    "file_path": file_path,
                    "status": "modified",
                    "diff": changes["changes"][file_path]["diff"]
                })
        
        for new_file in changes.get("new_files", []):
            applied_changes.append({
                "file_path": new_file["path"],
                "status": "created",
                "content": new_file["content"]
            })
        
        for deleted_file in changes.get("deleted_files", []):
            applied_changes.append({
                "file_path": deleted_file,
                "status": "deleted"
            })
        
        return applied_changes
    
    async def _generate_change_summary(self, 
                                     specification: str, 
                                     applied_changes: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the applied changes.
        
        Args:
            specification: The code change specification
            applied_changes: The list of applied changes
            
        Returns:
            A summary string
        """
        # This would typically use an LLM to generate a summary
        # For now, return a placeholder summary
        modified_count = sum(1 for change in applied_changes if change["status"] == "modified")
        created_count = sum(1 for change in applied_changes if change["status"] == "created")
        deleted_count = sum(1 for change in applied_changes if change["status"] == "deleted")
        
        return f"Applied changes for: {specification}\nModified {modified_count} files, created {created_count} files, deleted {deleted_count} files."
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities supported by this agent.
        
        Returns:
            A list of capability names
        """
        return ["code_implementation", "code_modification", "code_analysis", "code_generation"]