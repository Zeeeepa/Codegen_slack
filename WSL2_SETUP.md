# Running Bolt-Chat on WSL2 and Accessing from Windows

This guide explains how to run the Bolt-Chat Slack bot on WSL2 (Windows Subsystem for Linux) and access it from Windows.

## Prerequisites

1. WSL2 installed on your Windows machine
2. Ubuntu or another Linux distribution installed in WSL2
3. Python 3.8+ installed in your WSL2 environment
4. Slack app credentials (bot token, app token)

## Setup Steps

### 1. Install Dependencies in WSL2

Open your WSL2 terminal and navigate to the bolt-chat directory:

```bash
cd /path/to/bolt-chat
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure Port Forwarding

To access the bot from Windows, you need to set up port forwarding from WSL2 to Windows.

#### Automatic Port Forwarding (Recommended)

Create a script called `setup_port_forwarding.ps1` in your Windows home directory with the following content:

```powershell
# Get the WSL2 IP address
$wslIp = (wsl hostname -I).Trim()
Write-Host "WSL2 IP address: $wslIp"

# Set up port forwarding for the bot's port (default: 3000)
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=$wslIp

# Display the current port forwarding rules
netsh interface portproxy show all
```

Run this script as Administrator in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File setup_port_forwarding.ps1
```

#### Manual Port Forwarding

Alternatively, you can set up port forwarding manually:

1. Get the WSL2 IP address:
   ```bash
   wsl hostname -I
   ```

2. In an Administrator PowerShell, run:
   ```powershell
   netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=<WSL2_IP>
   ```

### 3. Configure Environment Variables

Create a `.env` file in your bolt-chat directory with the following content:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
PORT=3000
GITHUB_ACCESS_TOKEN=your-github-token
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 4. Configure Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and select your app
2. Under "Socket Mode", enable Socket Mode
3. Under "Event Subscriptions", enable events and add the following bot events:
   - `app_mention`
   - `message.im`
   - `message.channels` (if you want the bot to respond in channels)
4. Under "OAuth & Permissions", ensure the bot has the following scopes:
   - `app_mentions:read`
   - `chat:write`
   - `commands`
   - `files:read`
   - `files:write`
   - `im:history`
   - `im:read`
   - `im:write`

### 5. Run the Bot

Start the bot in your WSL2 terminal:

```bash
python app.py
```

The bot should now be running and accessible from both WSL2 and Windows.

## Accessing the Bot

- **From WSL2**: The bot is accessible at `http://localhost:3000`
- **From Windows**: The bot is accessible at `http://localhost:3000` (thanks to port forwarding)
- **From Slack**: The bot should be online and responding to messages and commands

## Troubleshooting

### Port Forwarding Issues

If you're having trouble with port forwarding:

1. Check if the WSL2 IP address has changed (it can change after reboots):
   ```bash
   wsl hostname -I
   ```

2. Update the port forwarding rule:
   ```powershell
   netsh interface portproxy delete v4tov4 listenport=3000 listenaddress=0.0.0.0
   netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=<NEW_WSL2_IP>
   ```

### Bot Not Responding

If the bot is not responding in Slack:

1. Check if the bot is running in WSL2
2. Verify that the Socket Mode is enabled in your Slack app
3. Check that the bot and app tokens are correct in your `.env` file
4. Restart the bot

### Codegen Integration Issues

If you're having issues with the Codegen integration:

1. Ensure the Codegen library is installed:
   ```bash
   pip install codegen
   ```

2. Check that the GitHub access token is set in your `.env` file
3. Verify that the repository you're trying to analyze exists and is accessible with your GitHub token

## Using the Codegen Agent

The Codegen agent provides powerful code analysis, search, and editing capabilities. Here are some example commands:

- Set the active repository:
  ```
  /codegen set-repo owner/repo
  ```

- Analyze code or answer questions:
  ```
  /codegen analyze How does the authentication system work?
  ```

- Search for code patterns:
  ```
  /codegen search function getUserById
  ```

- Generate code:
  ```
  /codegen generate Create a function to validate email addresses
  ```

- Edit code:
  ```
  /codegen edit src/auth.js: Add error handling to the login function
  ```