"""
Base agent class for bolt-chat.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    
    This class defines the common interface and functionality for all agent types.
    Specific agent implementations should inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new agent.
        
        Args:
            name: The name of the agent
            description: A brief description of the agent's purpose
            config: Optional configuration parameters for the agent
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.state: Dict[str, Any] = {}
        
    @abstractmethod
    async def process(self, 
                     input_data: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process input data and return a result.
        
        This is the main method that should be implemented by all agent subclasses.
        
        Args:
            input_data: The input data to process
            context: Optional context information
            
        Returns:
            A dictionary containing the processing result
        """
        pass
    
    async def initialize(self) -> None:
        """
        Initialize the agent.
        
        This method is called when the agent is first created or reset.
        Subclasses can override this method to perform initialization tasks.
        """
        self.state = {}
        
    async def cleanup(self) -> None:
        """
        Clean up resources used by the agent.
        
        This method is called when the agent is no longer needed.
        Subclasses can override this method to perform cleanup tasks.
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities supported by this agent.
        
        Returns:
            A list of capability names
        """
        return []
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update the agent's configuration.
        
        Args:
            config: The new configuration parameters
        """
        self.config.update(config)
        
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the agent.
        
        Returns:
            The agent's current state
        """
        return self.state
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        Set the agent's state.
        
        Args:
            state: The new state
        """
        self.state = state
        
    def __str__(self) -> str:
        """
        Get a string representation of the agent.
        
        Returns:
            A string representation
        """
        return f"{self.name}: {self.description}"