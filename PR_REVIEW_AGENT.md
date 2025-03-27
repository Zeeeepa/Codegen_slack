# PR Review Agent

The PR Review Agent is a powerful tool that automatically analyzes GitHub pull requests and provides detailed improvement suggestions. It uses AI to analyze code and always finds ways to make your code better, even if it already looks good.

## Features

- **Automatic PR Analysis**: Listens for GitHub webhook events and automatically analyzes PRs when they're created or updated
- **Manual Review Triggering**: Use the `/review-pr` command in Slack to manually trigger a review
- **AI-Powered Analysis**: Uses OpenAI or Anthropic to analyze code and provide detailed feedback
- **Multi-Repository Support**: Can monitor PRs from any number of repositories
- **Slack Notifications**: Sends notifications to Slack when PR reviews are completed

## Setup

### Environment Variables

The PR Review Agent requires the following environment variables:

```
# GitHub API Token (with repo scope)
GITHUB_TOKEN=your_github_token

# GitHub Webhook Secret (for verifying webhook payloads)
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Slack Bot Token
SLACK_BOT_TOKEN=your_slack_bot_token

# Slack App Token
SLACK_APP_TOKEN=your_slack_app_token

# Slack Notification Channel (optional, defaults to "general")
SLACK_NOTIFICATION_CHANNEL=your_slack_channel_id

# OpenAI API Key (for code analysis)
OPENAI_API_KEY=your_openai_api_key

# Anthropic API Key (fallback for code analysis)
ANTHROPIC_API_KEY=your_anthropic_api_key

# Port for the webhook server (optional, defaults to 3000)
PORT=3000
```

You can also use character-based API keys as described in the [CHARACTER_SETUP.md](CHARACTER_SETUP.md) file.

### GitHub Webhook Setup

1. Go to your GitHub repository settings
2. Click on "Webhooks" in the left sidebar
3. Click "Add webhook"
4. Set the Payload URL to `https://your-server-url/github/webhook`
5. Set the Content type to `application/json`
6. Set the Secret to the same value as your `GITHUB_WEBHOOK_SECRET` environment variable
7. Select "Let me select individual events" and check "Pull requests"
8. Click "Add webhook"

Repeat these steps for each repository you want to monitor.

### Slack Command Setup

1. Go to your Slack App settings at https://api.slack.com/apps
2. Click on your app
3. Click on "Slash Commands" in the left sidebar
4. Click "Create New Command"
5. Set the Command to `/review-pr`
6. Set the Request URL to `https://your-server-url/slack/events`
7. Set the Short Description to "Review a GitHub pull request"
8. Set the Usage Hint to "[repo_owner/repo_name PR_number] or [PR_URL]"
9. Click "Save"

## Usage

### Automatic PR Reviews

Once set up, the PR Review Agent will automatically analyze pull requests when they are:

- Opened
- Updated (new commits pushed)
- Reopened

The agent will post a review comment on the PR with detailed improvement suggestions.

### Manual PR Reviews

You can also manually trigger a PR review using the `/review-pr` Slack command:

```
/review-pr https://github.com/owner/repo/pull/123
```

Or:

```
/review-pr owner/repo 123
```

## How It Works

1. The PR Review Agent receives a webhook event from GitHub when a PR is opened, updated, or reopened
2. It fetches the PR details, including the files changed and the diff
3. It analyzes each file using AI (OpenAI or Anthropic) to find improvement suggestions
4. It posts a review comment on the PR with the analysis results
5. It sends a notification to Slack

## Customization

### AI Providers

The PR Review Agent uses OpenAI by default, with Anthropic as a fallback. You can customize this behavior by modifying the `analyze_code_with_ai` function in `github_integration/pr_analyzer.py`.

### Review Format

You can customize the format of the review by modifying the prompt in the `analyze_code_with_ai` function and the summary generation in the `analyze_pr` function.

### Notification Channel

You can customize the Slack notification channel by setting the `SLACK_NOTIFICATION_CHANNEL` environment variable.

## Troubleshooting

### Webhook Issues

- Make sure your webhook URL is publicly accessible
- Check that your webhook secret matches the `GITHUB_WEBHOOK_SECRET` environment variable
- Verify that you've selected the "Pull requests" event in your webhook settings

### API Token Issues

- Make sure your GitHub token has the `repo` scope
- Make sure your Slack tokens are correct
- Make sure your OpenAI or Anthropic API keys are valid

### Server Issues

- Make sure your server is running and accessible
- Check the logs for any errors
- Make sure the required environment variables are set