"""
Agent registry for managing different types of agents.
"""
import logging
from typing import Dict, Type, List

from .base_agent import BaseAgent
from .codegen_agent import CodegenAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Registry for managing agent types and instances.
    """
    _agents: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register_agent(cls, name: str, agent_class: Type[BaseAgent]):
        """
        Register an agent class with the registry.
        
        Args:
            name: The name of the agent
            agent_class: The agent class
        """
        cls._agents[name] = agent_class
        logger.info(f"Registered agent: {name}")
    
    @classmethod
    def get_agent(cls, name: str) -> Type[BaseAgent]:
        """
        Get an agent class by name.
        
        Args:
            name: The name of the agent
            
        Returns:
            The agent class
        """
        if name not in cls._agents:
            raise ValueError(f"Unknown agent: {name}")
        return cls._agents[name]
    
    @classmethod
    def get_available_agents(cls) -> List[str]:
        """
        Get a list of available agent names.
        
        Returns:
            A list of agent names
        """
        return list(cls._agents.keys())
    
    @classmethod
    def register_default_agents(cls):
        """
        Register default agents with the registry.
        """
        cls.register_agent("codegen", CodegenAgent)