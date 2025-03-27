# Slack AI Chatbot

This Slack chatbot app template offers a customizable solution for integrating AI-powered conversations into your Slack workspace. Here's what the app can do out of the box:

* Interact with the bot by mentioning it in conversations and threads
* Send direct messages to the bot for private interactions
* Use the `/ask-bolty` command to communicate with the bot in channels where it hasn't been added
* Utilize a custom function for integration with Workflow Builder to summarize messages in conversations
* Select your preferred API/model from the app home to customize the bot's responses
* Bring Your Own Language Model [BYO LLM](#byo-llm) for customization
* Support for [multiple API keys](#multi-instance) for OpenAI and Anthropic providers
* Support for [character-based API instances](#character-based) for creating different AI personas
* Custom FileStateStore creates a file in /data per user to store API/model preferences
* [PR Review Agent](#pr-review-agent) that automatically analyzes GitHub pull requests and provides improvement suggestions

Inspired by [ChatGPT-in-Slack](https://github.com/seratch/ChatGPT-in-Slack/tree/main)

Before getting started, make sure you have a development workspace where you have permissions to install apps. If you don't have one setup, go ahead and [create one](https://slack.com/create).
## Installation

#### Prerequisites
* To use the OpenAI and Anthropic models, you must have an account with sufficient credits.
* To use the Vertex models, you must have [a Google Cloud Provider project](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#expandable-1) with sufficient credits.

<a name="pr-review-agent"></a>
## PR Review Agent

The PR Review Agent is a powerful tool that automatically analyzes GitHub pull requests and provides detailed improvement suggestions. It uses AI to analyze code and always finds ways to make your code better, even if it already looks good.

### Features

- **Automatic PR Analysis**: Listens for GitHub webhook events and automatically analyzes PRs when they're created or updated
- **Manual Review Triggering**: Use the `/review-pr` command in Slack to manually trigger a review
- **AI-Powered Analysis**: Uses OpenAI or Anthropic to analyze code and provide detailed feedback
- **Multi-Repository Support**: Can monitor PRs from any number of repositories
- **Slack Notifications**: Sends notifications to Slack when PR reviews are completed

For detailed setup instructions and usage information, see [PR_REVIEW_AGENT.md](./PR_REVIEW_AGENT.md).
