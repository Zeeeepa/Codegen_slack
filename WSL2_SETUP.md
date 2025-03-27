# Running Bolt-Chat on WSL2 and Accessing from Windows

This guide explains how to run the Bolt-Chat Slack bot on WSL2 (Windows Subsystem for Linux) and access it from Windows.

## Prerequisites

1. WSL2 installed on your Windows machine
2. Ubuntu or another Linux distribution installed in WSL2
3. Python 3.8+ installed in your WSL2 environment
4. Slack app credentials (tokens, etc.)

## Setup Instructions

### 1. Install Dependencies in WSL2

Open your WSL2 terminal and navigate to the bolt-chat directory:

```bash
cd /path/to/bolt-chat
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure Network for Windows Access

By default, applications running in WSL2 are not directly accessible from Windows. To make the bot accessible, you need to:

#### Option 1: Port Forwarding (Recommended)

Set up port forwarding from Windows to WSL2:

1. Find your WSL2 IP address:

```bash
# In WSL2 terminal
ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
```

2. Set up port forwarding in Windows PowerShell (run as Administrator):

```powershell
# Replace <WSL2_IP_ADDRESS> with the IP address from step 1
# Replace <PORT> with the port your bot is running on (default: 3000)
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=<PORT> connectaddress=<WSL2_IP_ADDRESS> connectport=<PORT>
```

3. Allow the port through Windows Firewall:

```powershell
netsh advfirewall firewall add rule name="Bolt-Chat Bot" dir=in action=allow protocol=TCP localport=<PORT>
```

#### Option 2: Use WSL2 IP Directly

You can also access the WSL2 application directly using its IP address:

1. Find your WSL2 IP address as shown above
2. Use this IP address in your Slack app configuration

### 3. Configure Environment Variables

Create a `.env` file in your bolt-chat directory with the necessary environment variables:

```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
CODEGEN_API_URL=http://localhost:8000
CODEGEN_API_KEY=your-codegen-api-key
PORT=3000
```

### 4. Run the Bot

Start the bot in your WSL2 terminal:

```bash
python app.py
```

### 5. Configure Slack App

1. Go to your [Slack API Apps page](https://api.slack.com/apps)
2. Select your app
3. Under "Socket Mode", ensure it's enabled
4. Under "Event Subscriptions", add the necessary bot events
5. Under "Slash Commands", add the commands you want to use

## Troubleshooting

### WSL2 IP Address Changes

The WSL2 IP address may change after reboots. If you can't connect to your bot:

1. Check the current WSL2 IP address
2. Update your port forwarding rules

### Port Already in Use

If you get an error that the port is already in use:

```bash
# List processes using the port
sudo lsof -i :<PORT>

# Kill the process if needed
sudo kill <PID>
```

### Checking Port Forwarding

To verify your port forwarding is set up correctly:

```powershell
# In Windows PowerShell
netsh interface portproxy show all
```

### Resetting Port Forwarding

To remove port forwarding:

```powershell
# In Windows PowerShell (as Administrator)
netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=<PORT>
```

## Additional Resources

- [WSL2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Slack API Documentation](https://api.slack.com/)