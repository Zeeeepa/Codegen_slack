# PR Review Agent

This document explains how to set up and use the PR Review Agent in the Bolt Chat application.

## Overview

The PR Review Agent is a feature that automatically analyzes GitHub pull requests and provides constructive feedback and improvement suggestions. It can be triggered in two ways:

1. **Automatically via GitHub webhooks**: When a PR is opened or updated in a monitored repository
2. **Manually via Slack command**: Using the `/review-pr` command in Slack

## Features

- Automatic code analysis of PRs
- Detailed feedback on code quality, best practices, and potential issues
- Support for multiple repositories
- Slack notifications for PR reviews
- Manual review triggering via Slack command
- **Deep code research** for understanding code in its broader context
- **Q&A capability** to ask specific questions about the code in a PR

## Setup

### Environment Variables

The PR Review Agent requires the following environment variables:

```
# GitHub Configuration
GITHUB_TOKEN=your-github-token
GITHUB_WEBHOOK_SECRET=your-webhook-secret
PR_REVIEW_REPOS=owner/repo1,owner/repo2  # Optional, comma-separated list of repos to monitor

# AI Provider Configuration
PR_REVIEW_AI_PROVIDER=openai  # or anthropic
PR_REVIEW_OPENAI_MODEL=gpt-4  # Optional, defaults to gpt-4
PR_REVIEW_ANTHROPIC_MODEL=claude-3-opus-20240229  # Optional, defaults to claude-3-opus-20240229

# Slack Configuration
PR_REVIEW_SLACK_CHANNEL=#github-reviews  # Optional, defaults to #general
```

### GitHub Webhook Setup

1. Go to your GitHub repository or organization settings
2. Navigate to "Webhooks" and click "Add webhook"
3. Set the Payload URL to `https://your-bolt-app-url/github/webhook`
4. Set the Content type to `application/json`
5. Set the Secret to the same value as your `GITHUB_WEBHOOK_SECRET` environment variable
6. Select "Let me select individual events" and check "Pull requests"
7. Click "Add webhook"

## Usage

### Automatic PR Reviews

Once set up, the PR Review Agent will automatically analyze PRs when they are:
- Opened for the first time
- Updated with new commits

The agent will post its analysis as a comment on the PR and send a notification to the configured Slack channel.

### Manual PR Reviews

You can manually trigger a PR review using the `/review-pr` command in Slack:

```
/review-pr https://github.com/owner/repo/pull/123
```

Or using the shorter format:

```
/review-pr owner/repo#123
```

### Asking Questions About PR Code

You can ask specific questions about the code in a PR using the `/ask-pr-question` command in Slack:

```
/ask-pr-question https://github.com/owner/repo/pull/123 How does this code handle error cases?
```

Or using the shorter format:

```
/ask-pr-question owner/repo#123 What's the purpose of the new function?
```

The agent will analyze the PR code and provide a detailed answer to your question based on deep code research.

## Deep Code Research

The PR Review Agent uses Codegen's deep code research capabilities to analyze the code in its broader context. This allows it to:

1. Understand the relationships between different parts of the codebase
2. Identify potential issues that might not be apparent from looking at individual files
3. Suggest improvements based on patterns and best practices in the rest of the codebase
4. Explain how the changes impact the overall system

This deep understanding of the code enables the agent to provide more insightful and contextual feedback than traditional code review tools.

## Customization

### AI Provider

You can choose between OpenAI and Anthropic as the AI provider for PR reviews by setting the `PR_REVIEW_AI_PROVIDER` environment variable to either `openai` or `anthropic`.

### Monitored Repositories

By default, the PR Review Agent will monitor all repositories that send webhooks to it. You can restrict it to specific repositories by setting the `PR_REVIEW_REPOS` environment variable to a comma-separated list of repository names (e.g., `owner/repo1,owner/repo2`).

### Slack Notifications

You can customize the Slack channel for PR review notifications by setting the `PR_REVIEW_SLACK_CHANNEL` environment variable.

## Troubleshooting

### Webhook Issues

If webhooks aren't being received:
1. Check that the webhook is properly configured in GitHub
2. Verify that the `GITHUB_WEBHOOK_SECRET` matches the secret in GitHub
3. Ensure your application is publicly accessible

### Authentication Issues

If you see authentication errors:
1. Verify that your `GITHUB_TOKEN` is valid and has the necessary permissions
2. Check that the token has access to the repositories you're trying to monitor

### AI Provider Issues

If the AI analysis fails:
1. Verify that the appropriate API key is set (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`)
2. Check that the specified model is available for your account
3. Ensure you have sufficient API credits/quota
