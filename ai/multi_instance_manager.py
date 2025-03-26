import logging
from typing import Dict, List, Optional, Any
from .providers.openai import OpenAI_API
from .providers.anthropic import AnthropicAPI
from env_loader import get_api_keys

logger = logging.getLogger(__name__)

class MultiInstanceManager:
    """
    Manages multiple instances of API providers with different API keys.
    This allows for load balancing, fallback, and using multiple accounts.
    """
    
    def __init__(self):
        self.openai_instances: Dict[str, OpenAI_API] = {}
        self.anthropic_instances: Dict[str, AnthropicAPI] = {}
        self.initialize_instances()
    
    def initialize_instances(self):
        """Initialize all available API instances from environment variables."""
        # Initialize OpenAI instances
        openai_keys = get_api_keys("OPENAI")
        for instance_id in openai_keys:
            try:
                self.openai_instances[instance_id] = OpenAI_API(instance_id=instance_id)
                logger.info(f"Initialized OpenAI instance {instance_id}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI instance {instance_id}: {str(e)}")
        
        # Initialize Anthropic instances
        anthropic_keys = get_api_keys("ANTHROPIC")
        for instance_id in anthropic_keys:
            try:
                self.anthropic_instances[instance_id] = AnthropicAPI(instance_id=instance_id)
                logger.info(f"Initialized Anthropic instance {instance_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic instance {instance_id}: {str(e)}")
    
    def get_openai_instance(self, instance_id: Optional[str] = None) -> Optional[OpenAI_API]:
        """
        Get an OpenAI API instance by ID.
        
        Args:
            instance_id: The ID of the instance to get. If None, returns the default instance.
        
        Returns:
            An OpenAI_API instance, or None if no instance is available.
        """
        if instance_id and instance_id in self.openai_instances:
            return self.openai_instances[instance_id]
        elif "default" in self.openai_instances:
            return self.openai_instances["default"]
        elif self.openai_instances:
            # Return the first available instance
            return next(iter(self.openai_instances.values()))
        return None
    
    def get_anthropic_instance(self, instance_id: Optional[str] = None) -> Optional[AnthropicAPI]:
        """
        Get an Anthropic API instance by ID.
        
        Args:
            instance_id: The ID of the instance to get. If None, returns the default instance.
        
        Returns:
            An AnthropicAPI instance, or None if no instance is available.
        """
        if instance_id and instance_id in self.anthropic_instances:
            return self.anthropic_instances[instance_id]
        elif "default" in self.anthropic_instances:
            return self.anthropic_instances["default"]
        elif self.anthropic_instances:
            # Return the first available instance
            return next(iter(self.anthropic_instances.values()))
        return None
    
    def get_available_openai_instances(self) -> List[str]:
        """
        Get a list of available OpenAI instance IDs.
        
        Returns:
            A list of instance IDs.
        """
        return list(self.openai_instances.keys())
    
    def get_available_anthropic_instances(self) -> List[str]:
        """
        Get a list of available Anthropic instance IDs.
        
        Returns:
            A list of instance IDs.
        """
        return list(self.anthropic_instances.keys())
    
    def generate_response(self, 
                         provider: str, 
                         instance_id: Optional[str], 
                         model: str, 
                         prompt: str, 
                         system_content: str) -> str:
        """
        Generate a response using the specified provider and instance.
        
        Args:
            provider: The provider to use ('openai' or 'anthropic')
            instance_id: The instance ID to use, or None for default
            model: The model to use
            prompt: The prompt to send
            system_content: The system content to send
        
        Returns:
            The generated response text
        
        Raises:
            ValueError: If the provider or instance is invalid
        """
        if provider.lower() == 'openai':
            instance = self.get_openai_instance(instance_id)
            if not instance:
                raise ValueError(f"No valid OpenAI instance found for ID: {instance_id}")
            
            instance.set_model(model)
            return instance.generate_response(prompt, system_content)
            
        elif provider.lower() == 'anthropic':
            instance = self.get_anthropic_instance(instance_id)
            if not instance:
                raise ValueError(f"No valid Anthropic instance found for ID: {instance_id}")
            
            instance.set_model(model)
            return instance.generate_response(prompt, system_content)
            
        else:
            raise ValueError(f"Invalid provider: {provider}")

# Create a singleton instance
manager = MultiInstanceManager()