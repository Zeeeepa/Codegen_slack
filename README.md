# Bolt-Chat

Bolt-Chat is a Slack chatbot powered by AI models from Anthropic and OpenAI, with integrated Codegen capabilities for code analysis, generation, and editing.

## Features

- Chat with AI models (OpenAI, Anthropic)
- Code analysis, generation, and editing using Codegen
- GitHub integration for PR reviews
- Voice message transcription
- Thread-based conversations
- Multi-agent support

## Getting Started

### Prerequisites

- Python 3.8+
- Slack app credentials (Bot Token and App Token)
- OpenAI API key (optional)
- Anthropic API key (optional)
- GitHub access token (optional, for PR reviews)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Zeeeepa/bolt-chat.git
   cd bolt-chat
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your credentials:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   CODEGEN_DEFAULT_REPO=your-default-repo
   ```

### Running the Application

Run the application with:
```bash
python app.py
```

You will be prompted to select an agent. Choose the Codegen agent by entering the corresponding number (usually 1).

## Using the Codegen Agent

The Codegen agent allows you to analyze, generate, and edit code through natural language conversations in Slack. The agent processes natural language without requiring specific commands.

### Repository Parsing

When you first start the Codegen agent, it will begin parsing the repository specified in the `CODEGEN_DEFAULT_REPO` environment variable. This process can take a few minutes for larger repositories. During this time, the agent will respond with a message indicating that parsing is in progress.

You can check the parsing status at any time using the `/parsing-status` command in Slack.

### Example Interactions

Here are some examples of what you can do with the Codegen agent:

- **Code Analysis**: "Can you explain how the agent system works in this codebase?"
- **Code Search**: "Find all functions related to message processing"
- **Code Generation**: "Create a function to validate user input"
- **Code Editing**: "Update the error handling in the app_mentioned_callback function"

### Handling Parsing Errors

If you encounter a "Repository has not been parsed" error, you can:

1. Wait a few minutes and try again
2. Use the `/parsing-status` command to check the current parsing status
3. Ask the agent to "retry parsing" if the parsing has failed
4. Check the logs for more detailed error information

## Slack Commands

The following Slack commands are available:

- `/ask-bolty [message]` - Ask a question to the AI
- `/chat [message]` - Start a thread-based conversation
- `/summarize [thread_ts]` - Summarize a thread
- `/image [prompt]` - Generate an image
- `/parsing-status` - Check the status of repository parsing for the Codegen agent

## Running on WSL2

For detailed instructions on running the application on WSL2 and accessing it from Windows, see [WSL2_SETUP.md](WSL2_SETUP.md).

## Troubleshooting

### Repository Parsing Issues

If you encounter issues with repository parsing:

1. Make sure the `CODEGEN_DEFAULT_REPO` environment variable is set correctly (e.g., "Zeeeepa/bolt-chat")
2. Verify that you have the correct permissions for the repository
3. Use the `/parsing-status` command to check the current parsing status
4. Check the logs for any error messages
5. Ask the agent to "retry parsing" if the parsing has failed

### Slack App Not Responding

Make sure your Slack app is properly configured with the following:

1. Event subscriptions enabled
2. Bot token scopes: `app_mentions:read`, `channels:history`, `chat:write`, `im:history`, `im:read`, `im:write`, `commands`
3. Socket Mode enabled
4. Commands properly registered in your Slack app configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.