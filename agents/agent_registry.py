"""
Agent registry for registering and managing agent types.
"""

import logging
from typing import Dict, Type, List

from agents.base_agent import BaseAgent
from agents.agent_factory import AgentFactory
from agents.pr_reviewer_agent import PRReviewerAgent
from agents.researcher_agent import ResearcherAgent
from agents.planner_agent import PlannerAgent
from agents.code_applicator_agent import CodeApplicatorAgent
from agents.codegen_agent import CodegenAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Registry for agent types.
    
    This class provides methods for registering and managing agent types.
    """
    
    @classmethod
    def register_default_agents(cls) -> None:
        """
        Register the default agent types.
        """
        # Register PR Reviewer agent
        AgentFactory.register_agent_type("pr_reviewer", PRReviewerAgent)
        
        # Register Researcher agent
        AgentFactory.register_agent_type("researcher", ResearcherAgent)
        
        # Register Planner agent
        AgentFactory.register_agent_type("planner", PlannerAgent)
        
        # Register Code Applicator agent
        AgentFactory.register_agent_type("code_applicator", CodeApplicatorAgent)
        
        # Register Codegen agent
        AgentFactory.register_agent_type("codegen", CodegenAgent)
        
        logger.info("Registered default agent types")
    
    @classmethod
    def get_agent_types(cls) -> List[str]:
        """
        Get a list of all registered agent types.
        
        Returns:
            A list of agent type names
        """
        return AgentFactory.get_available_agent_types()
    
    @classmethod
    def register_agent_type(cls, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """
        Register a custom agent type.
        
        Args:
            agent_type: The type name for the agent
            agent_class: The agent class to register
        """
        AgentFactory.register_agent_type(agent_type, agent_class)
        logger.info(f"Registered custom agent type: {agent_type}")