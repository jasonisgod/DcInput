# DcInput

Read messages from a Discord text channel and automatically type them at the current cursor position on your computer.

## How It Works

1. A Discord bot connects to your Discord server
2. It listens for new messages in a specific text channel
3. When a new message arrives, it simulates keyboard input to type the message text at your current cursor position

## Setup Guide

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create a Discord Bot & Get Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** -> give it a name (e.g., "DcInput")
3. Go to the **"Bot"** tab on the left sidebar
4. Click **"Add Bot"** -> confirm
5. Under the **TOKEN** section, click **"Reset Token"** (or **"Copy"**)
6. **Save this token** -- you'll paste it into the config file

> **Important:** Under the "Privileged Gateway Intents" section, **enable "Message Content Intent"** -- this is required for the bot to read message content.

### Step 3: Get Your Channel ID

1. Open Discord -> go to **User Settings** (gear icon near your name)
2. Go to **Advanced** -> toggle **"Developer Mode"** ON
3. Go to your server and **right-click** on the text channel you want to monitor
4. Click **"Copy Channel ID"**

### Step 4: Invite Bot to Your Server

1. In the Discord Developer Portal, go to **OAuth2** -> **URL Generator**
2. Under **Scopes**, select **"bot"**
3. Under **Bot Permissions**, select:
   - **Read Messages / View Channels**
   - **Send Messages** (optional, for testing)
4. Copy the generated URL and open it in your browser
5. Select your server and click **"Authorize"**

### Step 5: Configure the Config File

Create (or edit) `app.config` in the project folder with the following content:

```ini
[DEFAULT]
DISCORD_BOT_TOKEN = YOUR_BOT_TOKEN_HERE
CHANNEL_ID = 123456789012345678
```

- `DISCORD_BOT_TOKEN` -- paste the bot token from Step 2
- `CHANNEL_ID` -- paste the channel ID from Step 3 (as a number, no quotes)

> `app.config` is already in `.gitignore`, so your token will not be committed to Git.

### Step 6: Run the Script

```bash
python discord_typer.py
```

The script will connect to Discord and start listening. Any new message in the specified channel will be typed at your cursor position.

## Usage Tips

- **Position your cursor** where you want the text to appear before someone sends a message
- The script types messages in the format: `[HH:MM:SS] AuthorName: message content`
- Press **Ctrl+C** in the terminal to stop the script
- The bot only processes **new messages** sent after the script starts running

## Requirements

- Python 3.8+
- Windows (uses Win32 API for keyboard simulation)
- `discord.py` library
