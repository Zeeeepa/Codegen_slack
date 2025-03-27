"""
Base agent class for all agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """
    Base class for all agents.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the agent.
        
        Args:
            **kwargs: Additional arguments for the agent
        """
        self.config = kwargs
    
    @abstractmethod
    def process_message(self, message: str, context: Optional[str] = None) -> str:
        """
        Process a message and return a response.
        
        Args:
            message: The message to process
            context: Optional context for the message
            
        Returns:
            The response message
        """
        pass
    
    @classmethod
    def get_name(cls) -> str:
        """
        Get the name of the agent.
        
        Returns:
            The agent name
        """
        return cls.__name__
    
    @classmethod
    def get_description(cls) -> str:
        """
        Get a description of the agent.
        
        Returns:
            The agent description
        """
        return cls.__doc__ or "No description available"