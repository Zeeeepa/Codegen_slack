from .base_provider import BaseAPIProvider
import anthropic
import os
import logging
from env_loader import get_api_keys

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class AnthropicAPI(BaseAPIProvider):
    MODELS = {
        "claude-3-5-sonnet-20240620": {
            "name": "Claude 3.5 Sonnet",
            "provider": "Anthropic",
            "max_tokens": 4096,  # or 8192 with the header anthropic-beta: max-tokens-3-5-sonnet-2024-07-15
        },
        "claude-3-sonnet-20240229": {"name": "Claude 3 Sonnet", "provider": "Anthropic", "max_tokens": 4096},
        "claude-3-haiku-20240307": {"name": "Claude 3 Haiku", "provider": "Anthropic", "max_tokens": 4096},
        "claude-3-opus-20240229": {"name": "Claude 3 Opus", "provider": "Anthropic", "max_tokens": 4096},
    }

    def __init__(self, character_name=None):
        """
        Initialize the Anthropic API provider.
        
        Args:
            character_name: Optional character name to specify which API key to use.
                         If None, uses the default API key.
        """
        self.api_keys = get_api_keys("ANTHROPIC")
        
        if character_name and character_name in self.api_keys:
            self.api_key = self.api_keys[character_name]
            self.character_name = character_name
        elif "default" in self.api_keys:
            self.api_key = self.api_keys["default"]
            self.character_name = "default"
        else:
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            self.character_name = "default"
        
        # Initialize the client
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            logger.warning(f"No API key found for Anthropic character '{character_name}'")

    @classmethod
    def get_available_characters(cls):
        """
        Get a list of available API key characters.
        
        Returns:
            A list of character names that can be used to initialize this provider.
        """
        return list(get_api_keys("ANTHROPIC").keys())

    def set_model(self, model_name: str):
        if model_name not in self.MODELS.keys():
            raise ValueError("Invalid model")
        self.current_model = model_name

    def get_models(self) -> dict:
        if self.api_key is not None:
            return self.MODELS
        else:
            return {}

    def generate_response(self, prompt: str, system_content: str) -> str:
        try:
            if not self.client:
                raise ValueError(f"No valid API key for Anthropic character '{self.character_name}'")
                
            response = self.client.messages.create(
                model=self.current_model,
                system=system_content,
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
                max_tokens=self.MODELS[self.current_model]["max_tokens"],
            )
            return response.content[0].text
        except anthropic.APIConnectionError as e:
            logger.error(f"Server could not be reached: {e.__cause__}")
            raise e
        except anthropic.RateLimitError as e:
            logger.error(f"A 429 status code was received. {e}")
            raise e
        except anthropic.AuthenticationError as e:
            logger.error(f"There's an issue with your API key. {e}")
            raise e
        except anthropic.APIStatusError as e:
            logger.error(f"Another non-200-range status code was received: {e.status_code}")
            raise e
