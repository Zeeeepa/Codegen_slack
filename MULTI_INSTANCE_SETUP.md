# Multi-Instance API Key Setup

This guide explains how to set up multiple API keys for OpenAI and Anthropic providers in the Bolt Chat application. This feature allows you to:

- Deploy up to 9 instances of each provider
- Use different API keys for different requests
- Distribute load across multiple accounts
- Implement fallback mechanisms

## Environment Variables Setup

To use multiple API keys, you need to set up environment variables with specific naming conventions:

### OpenAI API Keys

```
# Default OpenAI API key (optional, for backward compatibility)
OPENAI_API_KEY=sk-your-default-openai-key

# Multiple OpenAI API keys
OPENAI_API_KEY_1=sk-your-first-openai-key
OPENAI_API_KEY_2=sk-your-second-openai-key
OPENAI_API_KEY_3=sk-your-third-openai-key
# ... up to OPENAI_API_KEY_9
```

### Anthropic API Keys

```
# Default Anthropic API key (optional, for backward compatibility)
ANTHROPIC_API_KEY=sk-ant-your-default-anthropic-key

# Multiple Anthropic API keys
ANTHROPIC_API_KEY_1=sk-ant-your-first-anthropic-key
ANTHROPIC_API_KEY_2=sk-ant-your-second-anthropic-key
ANTHROPIC_API_KEY_3=sk-ant-your-third-anthropic-key
# ... up to ANTHROPIC_API_KEY_9
```

## Using Multiple Instances

### Listing Available Instances

Use the `/list-instances` command in Slack to see all available API key instances:

```
/list-instances
```

This will display a list of all configured instances for both OpenAI and Anthropic providers.

### Using a Specific Instance

To use a specific instance when sending a message, add the `instance_id` parameter to your command:

```
/chat instance_id=1 Your message here
```

or

```
/ask-bolty instance_id=2 model=gpt-4o Your message here
```

You can also specify a model to use with the `model` parameter.

## Implementation Details

The multi-instance feature works by:

1. Loading all API keys from environment variables during startup
2. Parsing command parameters to extract the `instance_id` and `model` parameters
3. Using the specified instance to generate the response

If no `instance_id` is specified, the system will use the default instance or fall back to the first available instance.

## Troubleshooting

If you encounter issues with the multi-instance feature:

1. Check that your environment variables are correctly set
2. Use the `/list-instances` command to verify that your instances are recognized
3. Check the application logs for any error messages related to API key initialization

## Limitations

- The current implementation supports up to 9 instances per provider
- Instance IDs must be numeric (1-9)
- The feature is only implemented for OpenAI and Anthropic providers