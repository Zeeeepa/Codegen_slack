"""
Agent factory for creating different types of agents.
"""

import logging
from typing import Dict, Any, Optional, Type, List

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AgentFactory:
    """
    Factory class for creating and managing agent instances.
    
    This class provides methods for registering agent types and creating
    agent instances based on configuration parameters.
    """
    
    # Registry of agent types
    _agent_types: Dict[str, Type[BaseAgent]] = {}
    
    @classmethod
    def register_agent_type(cls, agent_type: str, agent_class: Type[BaseAgent]) -> None:
        """
        Register an agent type with the factory.
        
        Args:
            agent_type: The type name for the agent
            agent_class: The agent class to register
        """
        cls._agent_types[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")
        
    @classmethod
    def create_agent(cls, 
                    agent_type: str, 
                    config: Optional[Dict[str, Any]] = None) -> BaseAgent:
        """
        Create a new agent instance of the specified type.
        
        Args:
            agent_type: The type of agent to create
            config: Optional configuration parameters for the agent
            
        Returns:
            A new agent instance
            
        Raises:
            ValueError: If the agent type is not registered
        """
        if agent_type not in cls._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agent_types[agent_type]
        agent = agent_class(config=config)
        logger.info(f"Created agent of type: {agent_type}")
        
        return agent
    
    @classmethod
    def get_available_agent_types(cls) -> List[str]:
        """
        Get a list of all registered agent types.
        
        Returns:
            A list of agent type names
        """
        return list(cls._agent_types.keys())
    
    @classmethod
    def get_agent_class(cls, agent_type: str) -> Optional[Type[BaseAgent]]:
        """
        Get the agent class for a specific agent type.
        
        Args:
            agent_type: The agent type name
            
        Returns:
            The agent class, or None if not found
        """
        return cls._agent_types.get(agent_type)