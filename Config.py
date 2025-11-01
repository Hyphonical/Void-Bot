# 📦 Built-in modules
import logging
import os

# Load .env file manually for BOT_TYPE detection
try:
	with open('.env', 'r') as f:
		for line in f:
			if '=' in line and not line.strip().startswith('#'):
				key, value = line.strip().split('=', 1)
				os.environ[key] = value
except FileNotFoundError:
	pass

# 👾 Discord modules
import discord

# <-- Logging Settings -->

# Global Log Level
LogLevel = logging.INFO

# Blacklisted Channels (by ID) - Messages from these channels won't be logged
BlacklistedChannels = [
	1340307785312632915,  # Console
	1340314725770330185,  # Chat Link
]

# <-- Discord Settings -->

# Discord Intents
Intents = discord.Intents.default()
Intents.message_content = True

# Command Prefix
CommandPrefix = '!'

# Bot Name
BotName = 'Void Bot'

# Message Cooldown (in seconds) - Prevents spamming commands/messages
MessageCooldown = 2

# <-- Minecraft Settings -->

ProtocolVersion = 766  # 1.20.5
DefaultServer = 'play.voidtales.win'
DefaultServerPort = 25565
PresenceUpdateInterval = 30

# <-- Player Stats Settings -->

FuzzyMatchingThreshold = 0.6

# <-- Live Status Settings -->

# Channel ID for live status updates
# Use different channel for test mode vs production
LiveStatusChannelID = (
	1308757047596154951  # Test channel
	if os.getenv('BOT_TYPE') == 'test'
	else 1342510703386296483  # Production channel
)

# Update interval for live status (in seconds)
LiveStatusUpdateInterval = 60

# File path for live status persistence
LiveStatusFile = 'live_status.json'

# <-- Suggestions Settings -->

# Channel ID for suggestion embeds
SuggestionChannelID = 1411614420089438238

# <-- Role Settings -->

# Admin role IDs - Users with these roles have full admin permissions
ADMIN_ROLE_IDS = [1290261005955235840, 1308763721316958261]

# Moderator role ID - Users with this role have moderator permissions
MODERATOR_ROLE_ID = 1264629488130723872

# <-- Ticket System Settings -->

# Category ID for ticket channels
TICKETS_CATEGORY_ID = 1308780597988036628

# Channel ID for ticket transcripts
TRANSCRIPT_CHANNEL_ID = 1308793574329946162

# <-- Bot Color Settings -->

# Primary color for embeds (pastel green, used across all cogs)
EMBED_COLOR = discord.Color(0xA0D6B4)  # Pastel Green
