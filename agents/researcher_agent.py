"""
Researcher agent for gathering information from various sources.
"""

import logging
import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ResearcherAgent(BaseAgent):
    """
    Agent for conducting research and gathering information.
    
    This agent can search the web, access documentation, and analyze
    information to provide comprehensive research results.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new researcher agent.
        
        Args:
            config: Optional configuration parameters
        """
        super().__init__(
            name="Researcher",
            description="Conducts research and gathers information from various sources",
            config=config
        )
        
        # Initialize research tools based on config
        self.search_providers = []
        self.max_results = config.get("max_results", 5) if config else 5
        self.max_depth = config.get("max_depth", 2) if config else 2
        
        # Initialize state
        self.state = {
            "search_history": [],
            "current_research": None,
            "research_results": {}
        }
    
    async def process(self, 
                     input_data: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a research request.
        
        Args:
            input_data: The input data containing research parameters
            context: Optional context information
            
        Returns:
            A dictionary containing the research results
        """
        logger.info("Processing research request")
        
        # Extract research parameters
        query = input_data.get("query")
        sources = input_data.get("sources", ["web", "docs"])
        max_results = input_data.get("max_results", self.max_results)
        max_depth = input_data.get("max_depth", self.max_depth)
        
        # Validate input
        if not query:
            raise ValueError("Research query must be provided")
        
        # Update state
        self.state["current_research"] = {
            "query": query,
            "sources": sources,
            "max_results": max_results,
            "max_depth": max_depth,
            "status": "in_progress"
        }
        
        # Add to search history
        self.state["search_history"].append(query)
        
        # Conduct research
        try:
            research_results = await self._conduct_research(query, sources, max_results, max_depth)
            
            # Update state
            self.state["current_research"]["status"] = "completed"
            self.state["research_results"][query] = research_results
            
            return {
                "success": True,
                "query": query,
                "results": research_results,
                "sources_used": sources,
                "result_count": len(research_results.get("items", [])),
                "summary": research_results.get("summary", "")
            }
        except Exception as e:
            logger.error(f"Error conducting research: {str(e)}")
            
            # Update state
            self.state["current_research"]["status"] = "failed"
            self.state["current_research"]["error"] = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "sources_attempted": sources
            }
    
    async def _conduct_research(self, 
                              query: str, 
                              sources: List[str], 
                              max_results: int, 
                              max_depth: int) -> Dict[str, Any]:
        """
        Conduct research on a query using specified sources.
        
        Args:
            query: The research query
            sources: List of sources to search
            max_results: Maximum number of results to return
            max_depth: Maximum depth of research
            
        Returns:
            A dictionary containing the research results
        """
        results = {
            "query": query,
            "items": [],
            "summary": "",
            "sources": {}
        }
        
        # Search each source
        for source in sources:
            source_results = await self._search_source(source, query, max_results, max_depth)
            if source_results:
                results["sources"][source] = source_results
                results["items"].extend(source_results.get("items", []))
        
        # Limit results
        results["items"] = results["items"][:max_results]
        
        # Generate summary
        results["summary"] = await self._generate_summary(results["items"])
        
        return results
    
    async def _search_source(self, 
                           source: str, 
                           query: str, 
                           max_results: int, 
                           max_depth: int) -> Optional[Dict[str, Any]]:
        """
        Search a specific source for information.
        
        Args:
            source: The source to search
            query: The search query
            max_results: Maximum number of results to return
            max_depth: Maximum depth of research
            
        Returns:
            A dictionary containing the search results, or None if the source is not supported
        """
        if source == "web":
            return await self._search_web(query, max_results)
        elif source == "docs":
            return await self._search_docs(query, max_results)
        elif source == "github":
            return await self._search_github(query, max_results)
        elif source == "academic":
            return await self._search_academic(query, max_results)
        
        return None
    
    async def _search_web(self, query: str, max_results: int) -> Dict[str, Any]:
        """
        Search the web for information.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            A dictionary containing the search results
        """
        # This would typically use a web search API
        # For now, return placeholder results
        return {
            "source": "web",
            "items": [
                {
                    "title": f"Web result 1 for '{query}'",
                    "url": "https://example.com/1",
                    "snippet": f"This is a sample result for the query '{query}'."
                },
                {
                    "title": f"Web result 2 for '{query}'",
                    "url": "https://example.com/2",
                    "snippet": f"Another sample result for the query '{query}'."
                }
            ][:max_results]
        }
    
    async def _search_docs(self, query: str, max_results: int) -> Dict[str, Any]:
        """
        Search documentation for information.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            A dictionary containing the search results
        """
        # This would typically search documentation sources
        # For now, return placeholder results
        return {
            "source": "docs",
            "items": [
                {
                    "title": f"Documentation result 1 for '{query}'",
                    "url": "https://docs.example.com/1",
                    "snippet": f"Documentation sample for the query '{query}'."
                }
            ][:max_results]
        }
    
    async def _search_github(self, query: str, max_results: int) -> Dict[str, Any]:
        """
        Search GitHub for information.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            A dictionary containing the search results
        """
        # This would typically use the GitHub API
        # For now, return placeholder results
        return {
            "source": "github",
            "items": [
                {
                    "title": f"GitHub result 1 for '{query}'",
                    "url": "https://github.com/example/repo1",
                    "snippet": f"GitHub sample for the query '{query}'."
                }
            ][:max_results]
        }
    
    async def _search_academic(self, query: str, max_results: int) -> Dict[str, Any]:
        """
        Search academic sources for information.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            A dictionary containing the search results
        """
        # This would typically search academic databases
        # For now, return placeholder results
        return {
            "source": "academic",
            "items": [
                {
                    "title": f"Academic result 1 for '{query}'",
                    "url": "https://academic.example.com/1",
                    "snippet": f"Academic sample for the query '{query}'."
                }
            ][:max_results]
        }
    
    async def _generate_summary(self, items: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of research results.
        
        Args:
            items: The research result items
            
        Returns:
            A summary string
        """
        # This would typically use an LLM to generate a summary
        # For now, return a placeholder summary
        return f"Found {len(items)} results. The information suggests..."
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities supported by this agent.
        
        Returns:
            A list of capability names
        """
        return ["research", "web_search", "documentation_search", "github_search", "academic_search"]