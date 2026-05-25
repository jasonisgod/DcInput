"""
Discord Text Channel Reader - Types messages at current cursor position
===============================================================
Reads messages from a Discord text channel and types them at the current
cursor position on the computer running this script.

=== SETUP INSTRUCTIONS ===

Step 1: Get Discord Bot Token
  1. Go to https://discord.com/developers/applications
  2. Click "New Application" and give it a name
  3. Go to the "Bot" tab on the left sidebar
  4. Click "Reset Token" or "Copy" to get your bot token
  5. Paste it below as DISCORD_BOT_TOKEN

Step 2: Get Channel ID
  1. Open Discord and go to your server
  2. Go to User Settings -> Advanced -> Enable "Developer Mode"
  3. Right-click on the text channel you want to read from
  4. Click "Copy Channel ID"
  5. Paste it below as CHANNEL_ID

Step 3: Invite Bot to Server
  1. In Discord Developer Portal, go to OAuth2 -> URL Generator
  2. Select "bot" scope
  3. Select "Read Messages" / "View Channels" and "Send Messages" permissions
  4. Use the generated URL to invite the bot to your server
"""

import discord
import asyncio
import time
import sys
import threading
import os
from datetime import datetime

# ============================================================
# CONFIGURATION - Loaded from app.config
# ============================================================
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.config")

def load_config():
    """Load KEY=VALUE pairs from config file (supports both with and without [DEFAULT] section)."""
    config = {}
    if not os.path.exists(CONFIG_FILE):
        return config
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and section headers
            if not line or line.startswith("[") or line.startswith("#") or line.startswith(";"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    return config

_config = load_config()
DISCORD_BOT_TOKEN = _config.get("DISCORD_BOT_TOKEN", "")
CHANNEL_ID_STR = _config.get("CHANNEL_ID", "0")
CHANNEL_ID = int(CHANNEL_ID_STR) if CHANNEL_ID_STR.isdigit() else 0
# ============================================================


# Track the last message we've seen to avoid re-typing old messages
last_message_id = None

# Flag to control the typing thread
typing_active = True


def type_text(text):
    """
    Types the given text at the current cursor position using keyboard simulation.
    Uses clipboard + Ctrl+V for any text containing non-ASCII characters (e.g. Chinese),
    and keybd_event for pure ASCII text.
    """
    # Check if text contains any non-ASCII characters
    needs_clipboard = any(ord(c) > 127 for c in text)

    if needs_clipboard:
        _type_via_clipboard(text)
    else:
        _type_via_keybd(text)


def _type_via_clipboard(text):
    """
    Type text by copying it to clipboard and pasting with Ctrl+V.
    Uses PowerShell to set clipboard content (reliable for Unicode/Chinese).
    """
    import subprocess
    import ctypes

    user32 = ctypes.windll.user32

    # Use PowerShell to set clipboard content with Unicode support
    try:
        # Escape the text for PowerShell
        escaped = text.replace("'", "''")
        ps_cmd = f'Set-Clipboard -Value \'{escaped}\''
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            timeout=5
        )
    except Exception as e:
        print(f"  [Warning] Clipboard error: {e}")
        return

    # Paste with Ctrl+V (minimal delays for speed)
    time.sleep(0.02)
    user32.keybd_event(0x11, 0, 0, 0)  # Ctrl down
    time.sleep(0.01)
    user32.keybd_event(0x56, 0, 0, 0)  # V down
    time.sleep(0.01)
    user32.keybd_event(0x56, 0, 0x0002, 0)  # V up
    time.sleep(0.01)
    user32.keybd_event(0x11, 0, 0x0002, 0)  # Ctrl up
    time.sleep(0.02)



def _type_via_keybd(text):
    """
    Type ASCII text using keybd_event for each character.
    """
    import ctypes

    user32 = ctypes.windll.user32
    VK_SHIFT = 0x10
    KEYEVENTF_KEYUP = 0x0002

    # Map of special characters to their shift-key equivalents
    shift_chars = {
        '~': '`', '!': '1', '@': '2', '#': '3', '$': '4',
        '%': '5', '^': '6', '&': '7', '*': '8', '(': '9',
        ')': '0', '_': '-', '+': '=', '{': '[', '}': ']',
        '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.',
        '?': '/'
    }

    # Map of characters to virtual key codes
    char_to_vk = {
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
        'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
        'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
        'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
        'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
        'z': 0x5A,
        '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
        '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
        ' ': 0x20, '.': 0xBE, ',': 0xBC, '?': 0xBF, '/': 0xBF,
        '\\': 0xDC, '[': 0xDB, ']': 0xDD, '-': 0xBD, '=': 0xBB,
        ';': 0xBA, "'": 0xDE, '`': 0xC0, '\n': 0x0D, '\r': 0x0D,
    }

    def press_key(vk_code):
        user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)

    def press_shift_key(vk_code):
        user32.keybd_event(VK_SHIFT, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.02)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)
        user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)

    for char in text:
        if char == '\n' or char == '\r':
            press_key(0x0D)
            continue

        if char.isupper():
            lower_char = char.lower()
            if lower_char in char_to_vk:
                press_shift_key(char_to_vk[lower_char])
        elif char in shift_chars:
            base = shift_chars[char]
            if base in char_to_vk:
                press_shift_key(char_to_vk[base])
        elif char in char_to_vk:
            press_key(char_to_vk[char])

        time.sleep(0.01)


class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f"\n{'='*60}")
        print(f"  Logged in as {self.user} (ID: {self.user.id})")
        print(f"  Monitoring channel ID: {CHANNEL_ID}")
        print(f"{'='*60}")
        print(f"  Waiting for new messages...")
        print(f"  (Messages will be typed at your cursor position)")
        print(f"{'='*60}\n")

    async def on_message(self, message):
        global last_message_id

        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        # Only process messages from the target channel
        if message.channel.id != CHANNEL_ID:
            return

        # Skip if we've already processed this message
        if last_message_id and message.id <= last_message_id:
            return

        # Update the last seen message ID
        last_message_id = message.id

        # Format the message with author info
        timestamp = message.created_at.strftime("%H:%M:%S")
        author = message.author.display_name
        content = message.content

        # Build the text to type (only the message content, no trailing newline)
        text_to_type = f"{content}"

        print(f"\n>>> New message from {author}:")
        print(f"    {content}")
        print(f"    Typing at cursor...")

        # Type the message at the current cursor position
        type_text(text_to_type)

        # Also handle attachments (just show a note)
        if message.attachments:
            for att in message.attachments:
                attachment_text = f"{att.filename}: {att.url}\n"
                type_text(attachment_text)


def run_bot():
    """Run the Discord bot."""
    intents = discord.Intents.default()
    intents.message_content = True  # Required to read message content

    client = DiscordClient(intents=intents)

    try:
        client.run(DISCORD_BOT_TOKEN, log_handler=None)
    except discord.LoginFailure:
        print("\n[ERROR] Invalid Discord bot token. Please check your token.")
        print("  Go to https://discord.com/developers/applications")
        print("  -> Your Application -> Bot -> Reset Token / Copy")
        os._exit(1)
    except discord.PrivilegedIntentsRequired:
        print("\n[ERROR] Message Content Intent is not enabled!")
        print("  Go to https://discord.com/developers/applications")
        print("  -> Your Application -> Bot -> Enable 'Message Content Intent'")
        os._exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        os._exit(1)




def main():
    print("=" * 60)
    print("  Discord Text Channel Reader & Typer")
    print("=" * 60)

    # Check configuration
    if not DISCORD_BOT_TOKEN:
        print("\n[!] DISCORD_BOT_TOKEN is not set!")
        print("    Please edit the script and paste your bot token.")
        print("    See instructions at the top of the script.\n")
        sys.exit(1)

    if not CHANNEL_ID:
        print("\n[!] CHANNEL_ID is not set!")
        print("    Please edit the script and paste your channel ID.")
        print("    See instructions at the top of the script.\n")
        sys.exit(1)

    print(f"\n  Bot Token: {DISCORD_BOT_TOKEN[:10]}...{DISCORD_BOT_TOKEN[-5:]}")
    print(f"  Channel ID: {CHANNEL_ID}")
    print(f"\n  Starting bot... (Press Ctrl+C to stop)\n")

    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
