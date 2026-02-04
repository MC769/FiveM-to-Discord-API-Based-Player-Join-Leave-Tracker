# FiveM-to-Discord-API-Based-Player-Join-Leave-Tracker
Discord bot that monitors a FiveM server in real time and sends automated player join/leave updates to a Discord channel using the official FiveM API.

🎮 FiveM Player Activity Discord Bot

A real-time Discord monitoring bot that tracks player activity on a FiveM server and automatically posts join/leave notifications to a designated Discord channel using rich embeds.
This bot fetches live server data directly from the official FiveM servers API, detects player changes, and keeps your community informed with clean, readable updates.

✨ Features

🔄 Real-time player tracking
✅ Detects players joining and leaving
📊 Displays current player count
🟢 Smart online/offline detection using lastSeen
⏱️ Configurable polling interval
🎨 Clean Discord embed notifications
🛡️ Error-handling for API and network failures

🛠️ Built With

Python 3
discord.py
FiveM Official Servers API
Async task loop for efficient polling

⚙️ How It Works

Polls the FiveM server API at a set interval
Extracts live player data
Compares current players with previous state
Sends Discord embed updates when changes occur

🚀 Use Cases

FiveM server owners & admins
Community Discord servers
Automated activity logging
Live server status monitoring

📌 Configuration

Update the following values in the script:

SERVER_CODE = "your_fivem_server_code"
DISCORD_BOT_TOKEN = "your_discord_bot_token"
DISCORD_CHANNEL_ID = your_channel_id
POLL_INTERVAL = 20

📜 License

This project is open-source and available for personal or community use.
