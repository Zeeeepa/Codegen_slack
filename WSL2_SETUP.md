# Running Bolt-Chat on WSL2

This guide will help you set up and run the Bolt-Chat application on WSL2 (Windows Subsystem for Linux) and access it from Windows.

## Prerequisites

1. WSL2 installed on your Windows machine
2. A Linux distribution (e.g., Ubuntu) installed on WSL2
3. Python 3.8+ installed on your WSL2 distribution
4. Slack app credentials (Bot Token and App Token)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Zeeeepa/bolt-chat.git
cd bolt-chat
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following environment variables to the `.env` file:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
CODEGEN_DEFAULT_REPO=your-default-repo
```

### 5. Port Forwarding for WSL2

To make the application accessible from Windows, you need to set up port forwarding. Create a PowerShell script named `wsl-port-forwarding.ps1` on your Windows machine:

```powershell
# Run this script as Administrator
$wslIp = (wsl hostname -I).Trim()
$ports = @(3000)  # Add more ports if needed

foreach ($port in $ports) {
    netsh interface portproxy delete v4tov4 listenport=$port listenaddress=0.0.0.0
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp
}

# Display the current port forwarding rules
netsh interface portproxy show all
```

Run this script as Administrator whenever you start WSL2 or if your WSL2 IP address changes.

### 6. Running the Application

In your WSL2 terminal, navigate to the bolt-chat directory and run:

```bash
python app.py
```

You will be prompted to select an agent. Choose the Codegen agent by entering the corresponding number.

### 7. Accessing the Application

The application will be accessible from both WSL2 and Windows:

- From WSL2: `http://localhost:3000`
- From Windows: `http://localhost:3000`

## Troubleshooting

### WSL2 IP Address Changes

The WSL2 IP address may change when you restart your computer. If you can't access the application from Windows, run the port forwarding script again.

### Slack App Not Responding

Make sure your Slack app is properly configured with the following:

1. Event subscriptions enabled
2. Bot token scopes: `app_mentions:read`, `channels:history`, `chat:write`, `im:history`, `im:read`, `im:write`
3. Socket Mode enabled

### Codegen Agent Issues

If the Codegen agent is not working properly, check the following:

1. Make sure the `CODEGEN_DEFAULT_REPO` environment variable is set correctly
2. Verify that you have the correct permissions for the repository
3. Check the logs for any error messages

## Additional Resources

- [Slack API Documentation](https://api.slack.com/docs)
- [WSL2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Codegen Documentation](https://github.com/codegen-sh/codegen)