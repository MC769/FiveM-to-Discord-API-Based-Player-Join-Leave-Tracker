import discord
from discord.ext import tasks
import requests
import asyncio
from datetime import datetime

# Configuration
SERVER_CODE = " "  # Your FiveM server code
API_URL = f"https://servers-frontend.fivem.net/api/servers/single/{SERVER_CODE}"
DISCORD_BOT_TOKEN = " "
DISCORD_CHANNEL_ID =   # Replace with your channel ID
POLL_INTERVAL = 20  # Check every 60 seconds

# Initialize
previous_players = set()
client = discord.Client(intents=discord.Intents.default())

def get_server_data():
    """Fetch player data directly from FiveM API"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        server_data = data.get("Data", {})
        
        if server_data:
            last_seen = server_data.get("lastSeen", "")
            is_online = check_server_online(last_seen)
            
            if is_online:
                players_list = server_data.get("players", [])
                player_names = [player.get("name", "Unknown") for player in players_list]
                current_players = set(player_names)
                player_count = server_data.get("clients", 0)
                return current_players, player_count, True
            else:
                print("Server appears offline (last seen > 5 min ago)")
                return set(), 0, False
        else:
            print("No server data found in response")
            return set(), 0, False
            
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching server data: {e}")
        return set(), 0, False
    except Exception as e:
        print(f"Error parsing server data: {e}")
        return set(), 0, False

def check_server_online(last_seen_str):
    """Check if server is online based on lastSeen timestamp"""
    try:
        from datetime import datetime, timezone, timedelta
        import re
        
        if not last_seen_str:
            return False
        
        if len(last_seen_str) > 26:  
            match = re.search(r'\.(\d+)(\+|Z|$)', last_seen_str)
            if match:
                microsec = match.group(1)
                if len(microsec) > 6:
                    last_seen_str = last_seen_str.replace(
                        f'.{microsec}', 
                        f'.{microsec[:6]}'
                    )
        
        if last_seen_str.endswith('Z'):
            last_seen_str = last_seen_str[:-1] + '+00:00'
        
        last_seen = datetime.fromisoformat(last_seen_str)
        
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        
        current_time = datetime.now(timezone.utc)
        
        # Consider server online if last seen within 5 minutes
        time_diff = (current_time - last_seen).total_seconds()
        return time_diff <= 300  # 5 minutes in seconds
        
    except Exception as e:
        print(f"Error checking server online status: {e}")
        print(f"Timestamp was: {last_seen_str}")
        return True

@client.event
async def on_ready():
    print(f'Discord bot logged in as {client.user}')
    print(f'Monitoring server: {SERVER_CODE}')
    check_players.start()

@tasks.loop(seconds=POLL_INTERVAL)
async def check_players():
    """Main task that checks for player changes"""
    global previous_players
    
    try:
        current_players, player_count, is_online = get_server_data()
        
        if not is_online:
            # Server is offline, skip checking
            return
        
        # Skip if no players and we haven't seen any before
        if not current_players and not previous_players:
            return
        
        # Find differences
        new_players = current_players - previous_players
        left_players = previous_players - current_players
        
        if new_players or left_players:
            channel = client.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                message = format_notification(new_players, left_players, player_count)
                await channel.send(embed=message)
                print(f"Sent update: {len(new_players)} joined, {len(left_players)} left")
        
        if current_players or previous_players: 
            previous_players = current_players
        
    except Exception as e:
        print(f"Error in check_players task: {e}")

def format_notification(new_players, left_players, player_count):
    """Format a nice Discord message for player changes"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    embed = discord.Embed(
        title="🎮 Player Activity Update",
        description=f"`[{timestamp}]`",
        color=discord.Color.green() if new_players else discord.Color.orange()
    )
    
    if new_players:
        players_str = "\n".join([f"• {player}" for player in sorted(new_players)])
        embed.add_field(
            name=f"✅ Joined ({len(new_players)})",
            value=players_str if players_str else "No new players",
            inline=False
        )
    
    if left_players:
        players_str = "\n".join([f"• {player}" for player in sorted(left_players)])
        embed.add_field(
            name=f"🚪 Left ({len(left_players)})",
            value=players_str if players_str else "No players left",
            inline=False
        )
    
    embed.add_field(
        name="📊 Current Status",
        value=f"**Total Players:** {player_count}",
        inline=False
    )
    
    embed.set_footer(text=f"Server: {SERVER_CODE}")
    
    return embed

if __name__ == "__main__":
    print("Testing FiveM API connection...")
    test_players, test_count, test_online = get_server_data()
    
    if test_online:
        print(f"✓ API connected successfully!")
        print(f"✓ Server is online with {test_count} players")
        print(f"✓ Player names: {sorted(test_players)}")
    else:
        print("⚠ Could not connect to server or server is offline")
        print("The bot will still start but won't send updates until server is online")
    
    print(f"\nStarting Discord bot...")
    print("Make sure you've updated:")
    print(f"1. SERVER_CODE: {SERVER_CODE}")
    print(f"2. DISCORD_BOT_TOKEN: {'SET' if DISCORD_BOT_TOKEN != 'your_discord_bot_token_here' else 'NOT SET'}")
    print(f"3. DISCORD_CHANNEL_ID: {'SET' if DISCORD_CHANNEL_ID != 123456789012345678 else 'NOT SET'}")
    
    client.run(DISCORD_BOT_TOKEN)
