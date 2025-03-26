import logging
from typing import Dict, List, Optional, Any
from .providers.openai import OpenAI_API
from .providers.anthropic import AnthropicAPI
from env_loader import get_api_keys

logger = logging.getLogger(__name__)

class CharacterInstanceManager:
    """
    Manages character-based instances of API providers with different API keys.
    Each character has its own API key and personality.
    """
    
    def __init__(self):
        self.openai_characters: Dict[str, OpenAI_API] = {}
        self.anthropic_characters: Dict[str, AnthropicAPI] = {}
        self.initialize_characters()
    
    def initialize_characters(self):
        """Initialize all available character API instances from environment variables."""
        # Initialize OpenAI characters
        openai_keys = get_api_keys("OPENAI")
        for character_name in openai_keys:
            try:
                self.openai_characters[character_name] = OpenAI_API(character_name=character_name)
                logger.info(f"Initialized OpenAI character '{character_name}'")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI character '{character_name}': {str(e)}")
        
        # Initialize Anthropic characters
        anthropic_keys = get_api_keys("ANTHROPIC")
        for character_name in anthropic_keys:
            try:
                self.anthropic_characters[character_name] = AnthropicAPI(character_name=character_name)
                logger.info(f"Initialized Anthropic character '{character_name}'")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic character '{character_name}': {str(e)}")
    
    def get_openai_character(self, character_name: Optional[str] = None) -> Optional[OpenAI_API]:
        """
        Get an OpenAI API character by name.
        
        Args:
            character_name: The name of the character to get. If None, returns the default character.
        
        Returns:
            An OpenAI_API instance, or None if no character is available.
        """
        if character_name and character_name in self.openai_characters:
            return self.openai_characters[character_name]
        elif "default" in self.openai_characters:
            return self.openai_characters["default"]
        elif self.openai_characters:
            # Return the first available character
            return next(iter(self.openai_characters.values()))
        return None
    
    def get_anthropic_character(self, character_name: Optional[str] = None) -> Optional[AnthropicAPI]:
        """
        Get an Anthropic API character by name.
        
        Args:
            character_name: The name of the character to get. If None, returns the default character.
        
        Returns:
            An AnthropicAPI instance, or None if no character is available.
        """
        if character_name and character_name in self.anthropic_characters:
            return self.anthropic_characters[character_name]
        elif "default" in self.anthropic_characters:
            return self.anthropic_characters["default"]
        elif self.anthropic_characters:
            # Return the first available character
            return next(iter(self.anthropic_characters.values()))
        return None
    
    def get_available_openai_characters(self) -> List[str]:
        """
        Get a list of available OpenAI character names.
        
        Returns:
            A list of character names.
        """
        return list(self.openai_characters.keys())
    
    def get_available_anthropic_characters(self) -> List[str]:
        """
        Get a list of available Anthropic character names.
        
        Returns:
            A list of character names.
        """
        return list(self.anthropic_characters.keys())
    
    def generate_response(self, 
                         provider: str, 
                         character_name: Optional[str], 
                         model: str, 
                         prompt: str, 
                         system_content: str) -> str:
        """
        Generate a response using the specified provider and character.
        
        Args:
            provider: The provider to use ('openai' or 'anthropic')
            character_name: The character name to use, or None for default
            model: The model to use
            prompt: The prompt to send
            system_content: The system content to send
        
        Returns:
            The generated response text
        
        Raises:
            ValueError: If the provider or character is invalid
        """
        if provider.lower() == 'openai':
            character = self.get_openai_character(character_name)
            if not character:
                raise ValueError(f"No valid OpenAI character found for name: {character_name}")
            
            character.set_model(model)
            return character.generate_response(prompt, system_content)
            
        elif provider.lower() == 'anthropic':
            character = self.get_anthropic_character(character_name)
            if not character:
                raise ValueError(f"No valid Anthropic character found for name: {character_name}")
            
            character.set_model(model)
            return character.generate_response(prompt, system_content)
            
        else:
            raise ValueError(f"Invalid provider: {provider}")

# Create a singleton instance
manager = CharacterInstanceManager()