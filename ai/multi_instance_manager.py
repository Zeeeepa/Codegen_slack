"""
Multi-instance manager for managing multiple AI provider instances.
This module provides a singleton manager for handling different AI provider instances,
including character-specific instances for OpenAI and Anthropic.
"""
import logging
from typing import Dict, Optional, List, Any

logger = logging.getLogger(__name__)

class MultiInstanceManager:
    """
    Manager for multiple AI provider instances.
    """
    def __init__(self):
        """
        Initialize the manager.
        """
        self._openai_characters = {}
        self._anthropic_characters = {}
        logger.info("Initialized MultiInstanceManager")
    
    def get_available_openai_characters(self) -> List[str]:
        """
        Get a list of available OpenAI character names.
        
        Returns:
            A list of character names
        """
        return list(self._openai_characters.keys())
    
    def get_available_anthropic_characters(self) -> List[str]:
        """
        Get a list of available Anthropic character names.
        
        Returns:
            A list of character names
        """
        return list(self._anthropic_characters.keys())
    
    def get_openai_character(self, name: str) -> Optional[Any]:
        """
        Get an OpenAI character instance by name.
        
        Args:
            name: The name of the character
            
        Returns:
            The character instance or None if not found
        """
        return self._openai_characters.get(name)
    
    def get_anthropic_character(self, name: str) -> Optional[Any]:
        """
        Get an Anthropic character instance by name.
        
        Args:
            name: The name of the character
            
        Returns:
            The character instance or None if not found
        """
        return self._anthropic_characters.get(name)
    
    def register_openai_character(self, name: str, instance: Any):
        """
        Register an OpenAI character instance.
        
        Args:
            name: The name of the character
            instance: The character instance
        """
        self._openai_characters[name] = instance
        logger.info(f"Registered OpenAI character: {name}")
    
    def register_anthropic_character(self, name: str, instance: Any):
        """
        Register an Anthropic character instance.
        
        Args:
            name: The name of the character
            instance: The character instance
        """
        self._anthropic_characters[name] = instance
        logger.info(f"Registered Anthropic character: {name}")
    
    def generate_response(self, provider: str, character_name: str, model: str, prompt: str, system_content: str) -> str:
        """
        Generate a response using a specific character.
        
        Args:
            provider: The provider name (openai or anthropic)
            character_name: The character name
            model: The model name
            prompt: The prompt text
            system_content: The system content
            
        Returns:
            The generated response
        """
        if provider.lower() == "openai":
            character = self.get_openai_character(character_name)
            if not character:
                raise ValueError(f"Unknown OpenAI character: {character_name}")
            character.set_model(model)
            return character.generate_response(prompt, system_content)
        elif provider.lower() == "anthropic":
            character = self.get_anthropic_character(character_name)
            if not character:
                raise ValueError(f"Unknown Anthropic character: {character_name}")
            character.set_model(model)
            return character.generate_response(prompt, system_content)
        else:
            raise ValueError(f"Unsupported provider for character generation: {provider}")

# Create a singleton instance
manager = MultiInstanceManager()