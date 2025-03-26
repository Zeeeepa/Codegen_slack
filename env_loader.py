import os
import logging
import re
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

def load_environment_variables():
    """
    Load and normalize environment variables for the application.
    This ensures compatibility between different naming conventions.
    Supports character-based API instances.
    """
    # Load environment variables from .env file if it exists
    env_path = Path('.') / '.env'
    if env_path.exists():
        logger.info(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        logger.warning("No .env file found. Using environment variables from the system.")
    
    # Process character-based API keys for OpenAI
    openai_characters = {}
    for key, value in os.environ.items():
        # Match OPENAI_CHARACTER_NAME, where NAME is the character name
        match = re.match(r'OPENAI_CHARACTER_([A-Za-z0-9_]+)', key)
        if match:
            character_name = match.group(1)
            openai_characters[character_name] = value
    
    # Store the keys in a structured format
    if openai_characters:
        os.environ["OPENAI_CHARACTER_KEYS"] = ",".join([f"{k}:{v}" for k, v in openai_characters.items()])
        logger.info(f"Loaded {len(openai_characters)} OpenAI character API keys")
    
    # Process character-based API keys for Anthropic
    anthropic_characters = {}
    for key, value in os.environ.items():
        # Match ANTHROPIC_CHARACTER_NAME, where NAME is the character name
        match = re.match(r'ANTHROPIC_CHARACTER_([A-Za-z0-9_]+)', key)
        if match:
            character_name = match.group(1)
            anthropic_characters[character_name] = value
    
    # Store the keys in a structured format
    if anthropic_characters:
        os.environ["ANTHROPIC_CHARACTER_KEYS"] = ",".join([f"{k}:{v}" for k, v in anthropic_characters.items()])
        logger.info(f"Loaded {len(anthropic_characters)} Anthropic character API keys")
    
    # Map OPENAI_* variables to LOCALAI_* variables if they don't exist
    if not os.environ.get("LOCALAI_API_KEY") and os.environ.get("OPENAI_API_KEY"):
        os.environ["LOCALAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
        logger.info("Using OPENAI_API_KEY for LOCALAI_API_KEY")
    
    if not os.environ.get("LOCALAI_API_URL") and os.environ.get("OPENAI_BASE_URL"):
        os.environ["LOCALAI_API_URL"] = os.environ.get("OPENAI_BASE_URL")
        logger.info("Using OPENAI_BASE_URL for LOCALAI_API_URL")
    
    if not os.environ.get("LOCALAI_MODEL") and os.environ.get("OPENAI_MODEL"):
        os.environ["LOCALAI_MODEL"] = os.environ.get("OPENAI_MODEL")
        logger.info("Using OPENAI_MODEL for LOCALAI_MODEL")
    
    # Log the configuration
    logger.info(f"API URL: {os.environ.get('LOCALAI_API_URL', os.environ.get('OPENAI_BASE_URL', 'Not set'))}")
    logger.info(f"Model: {os.environ.get('LOCALAI_MODEL', os.environ.get('OPENAI_MODEL', 'Not set'))}")
    
    # Mask API keys for logging
    api_key = os.environ.get("LOCALAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    if api_key:
        masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
        logger.info(f"API Key: {masked_key}")
    else:
        logger.warning("No API key found in environment variables")
    
    # Log number of character API keys
    if "OPENAI_CHARACTER_KEYS" in os.environ:
        logger.info(f"OpenAI character API keys available: {len(openai_characters)}")
    
    if "ANTHROPIC_CHARACTER_KEYS" in os.environ:
        logger.info(f"Anthropic character API keys available: {len(anthropic_characters)}")

def get_api_keys(provider_name):
    """
    Get all API keys for a specific provider.
    
    Args:
        provider_name: The name of the provider (e.g., 'OPENAI', 'ANTHROPIC')
    
    Returns:
        A dictionary of character_name -> api_key pairs
    """
    # First check for character-based keys
    character_keys_env_var = f"{provider_name}_CHARACTER_KEYS"
    if character_keys_env_var in os.environ and os.environ[character_keys_env_var]:
        keys_str = os.environ[character_keys_env_var]
        keys_dict = {}
        for key_pair in keys_str.split(","):
            if ":" in key_pair:
                character_name, api_key = key_pair.split(":", 1)
                keys_dict[character_name] = api_key
        return keys_dict
    
    # Fall back to the single API key if available
    single_key_env_var = f"{provider_name}_API_KEY"
    if single_key_env_var in os.environ and os.environ[single_key_env_var]:
        return {"default": os.environ[single_key_env_var]}
    
    return {}