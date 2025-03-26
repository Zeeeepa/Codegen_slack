# Character-Based API Setup

This guide explains how to set up and use character-based API instances in the Bolt Chat application.

## What are Character-Based API Instances?

Character-based API instances allow you to create different "characters" with their own API keys and personalities. Each character can have its own API key for OpenAI or Anthropic, allowing you to:

1. Create different AI personas (e.g., "Sherlock", "Watson", "Chef", "Programmer")
2. Use different API keys for different purposes
3. Organize your API usage by character

## Setting Up Character-Based API Keys

### Environment Variables

To set up character-based API keys, you need to define environment variables with the following naming pattern:

```
OPENAI_CHARACTER_NAME=your-api-key
ANTHROPIC_CHARACTER_NAME=your-api-key
```

Where `NAME` is the name of your character. For example:

```
OPENAI_CHARACTER_SHERLOCK=sk-abc123...
ANTHROPIC_CHARACTER_WATSON=sk-xyz789...
```

You can set these environment variables in your `.env` file or in your system environment.

### Example .env File

```
# Default API keys (used when no character is specified)
OPENAI_API_KEY=sk-default-openai-key
ANTHROPIC_API_KEY=sk-default-anthropic-key

# Character-based API keys for OpenAI
OPENAI_CHARACTER_SHERLOCK=sk-sherlock-openai-key
OPENAI_CHARACTER_PROGRAMMER=sk-programmer-openai-key

# Character-based API keys for Anthropic
ANTHROPIC_CHARACTER_WATSON=sk-watson-anthropic-key
ANTHROPIC_CHARACTER_CHEF=sk-chef-anthropic-key
```

## Using Character-Based API Instances

### Listing Available Characters

Use the `/list-instances` command in Slack to see all available character API instances:

```
/list-instances
```

This will show you a list of all available characters for both OpenAI and Anthropic.

### Using a Specific Character

To use a specific character, add the `character` parameter when using the chat commands:

```
/chat character=Sherlock model=gpt-4o Your prompt here
```

```
/chat-anthropic character=Watson model=claude-3-opus-20240229 Your prompt here
```

If you don't specify a character, the default API key will be used.

## Character-Based System Prompts (Future Enhancement)

In a future update, we plan to add support for character-specific system prompts. This will allow you to define different personalities and behaviors for each character.

## Troubleshooting

If you're having trouble with character-based API instances, check the following:

1. Make sure your environment variables are correctly formatted
2. Verify that your API keys are valid
3. Check the application logs for any error messages
4. Use the `/list-instances` command to verify that your characters are recognized

If you continue to have issues, please contact the administrator for assistance.