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

You will be prompted to select an agent. Choose the Codegen agent by entering the corresponding number.

## Using the Codegen Agent

The Codegen agent allows you to analyze, generate, and edit code through natural language conversations in Slack. Here are some examples of what you can do:

- **Code Analysis**: "Can you explain how the agent system works in this codebase?"
- **Code Search**: "Find all functions related to message processing"
- **Code Generation**: "Create a function to validate user input"
- **Code Editing**: "Update the error handling in the app_mentioned_callback function"

## Running on WSL2

For detailed instructions on running the application on WSL2 and accessing it from Windows, see [WSL2_SETUP.md](WSL2_SETUP.md).

## Troubleshooting

### Repository Not Parsed Error

If you encounter a "Repository has not been parsed" error, it means the Codegen agent is still initializing and parsing the repository. Wait a few moments and try again. If the error persists, check the following:

1. Make sure the `CODEGEN_DEFAULT_REPO` environment variable is set correctly
2. Verify that you have the correct permissions for the repository
3. Check the logs for any error messages

### Slack App Not Responding

Make sure your Slack app is properly configured with the following:

1. Event subscriptions enabled
2. Bot token scopes: `app_mentions:read`, `channels:history`, `chat:write`, `im:history`, `im:read`, `im:write`
3. Socket Mode enabled

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.