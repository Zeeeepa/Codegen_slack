from typing import List, Optional, Dict, Any, Tuple

from state_store.get_user_state import get_user_state

from ..ai_constants import DEFAULT_SYSTEM_CONTENT
from .anthropic import AnthropicAPI
from .openai import OpenAI_API
from .vertexai import VertexAPI
from .localai import LocalAI_API
from ..multi_instance_manager import manager

"""
New AI providers must be added below.
`get_available_providers()`
This function retrieves available API models from different AI providers.
It combines the available models into a single dictionary.
`_get_provider()`
This function returns an instance of the appropriate API provider based on the given provider name.
`get_provider_response`()
This function retrieves the user's selected API provider and model,
sets the model, and generates a response.
Note that context is an optional parameter because some functionalities,
such as commands, do not allow access to conversation history if the bot
isn't in the channel where the command is run.
"""


def get_available_providers():
    # Get models from all providers
    models = {}
    
    # Add models from OpenAI characters
    for character_name in manager.get_available_openai_characters():
        character = manager.get_openai_character(character_name)
        if character:
            for model_id, model_info in character.get_models().items():
                models[model_id] = model_info
    
    # Add models from Anthropic characters
    for character_name in manager.get_available_anthropic_characters():
        character = manager.get_anthropic_character(character_name)
        if character:
            for model_id, model_info in character.get_models().items():
                models[model_id] = model_info
    
    # Add models from other providers
    models.update(VertexAPI().get_models())
    models.update(LocalAI_API().get_models())
    
    return models


def _get_provider(provider_name: str, character_name: Optional[str] = None):
    """
    Get a provider instance.
    
    Args:
        provider_name: The name of the provider
        character_name: Optional character name for providers that support multiple characters
    
    Returns:
        A provider instance
    """
    if provider_name.lower() == "anthropic":
        if character_name:
            return manager.get_anthropic_character(character_name)
        return AnthropicAPI()
    elif provider_name.lower() == "openai":
        if character_name:
            return manager.get_openai_character(character_name)
        return OpenAI_API()
    elif provider_name.lower() == "vertexai":
        return VertexAPI()
    elif provider_name.lower() in ["localai", "deepinfra"]:
        return LocalAI_API()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def parse_command_args(text: str) -> Tuple[Dict[str, str], str]:
    """
    Parse command arguments from text.
    
    Args:
        text: The command text
    
    Returns:
        A tuple of (args_dict, remaining_text)
    """
    args = {}
    parts = text.split()
    remaining_parts = []
    
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            args[key.lower()] = value
        else:
            remaining_parts.append(part)
    
    return args, " ".join(remaining_parts)


def get_provider_response(user_id: str, prompt: str, context: Optional[List] = [], system_content=DEFAULT_SYSTEM_CONTENT):
    formatted_context = "\n".join([f"{msg['user']}: {msg['text']}" for msg in context])
    
    # Check if prompt contains character parameter
    args, remaining_text = parse_command_args(prompt)
    character_name = args.get("character")
    model_override = args.get("model")
    
    # Use remaining text as prompt if args were extracted
    if args:
        prompt = remaining_text
    
    full_prompt = f"Prompt: {prompt}\nContext: {formatted_context}"
    
    try:
        provider_name, model_name = get_user_state(user_id, False)
        
        # Override model if specified in args
        if model_override:
            model_name = model_override
        
        # Use the character instance manager if character_name is provided
        if character_name:
            response = manager.generate_response(
                provider=provider_name,
                character_name=character_name,
                model=model_name,
                prompt=full_prompt,
                system_content=system_content
            )
        else:
            # Use the traditional approach
            provider = _get_provider(provider_name)
            provider.set_model(model_name)
            response = provider.generate_response(full_prompt, system_content)
            
        return response
    except Exception as e:
        raise e
