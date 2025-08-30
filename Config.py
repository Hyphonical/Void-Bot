# 📦 Built-in modules
import logging

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
MessageCooldown = 5

# <-- Minecraft Settings -->

ProtocolVersion = 766  # 1.20.5
DefaultServer = 'play.voidtales.win'
DefaultServerPort = 25565
PresenceUpdateInterval = 30

# <-- Player Stats Settings -->

FuzzyMatchingThreshold = 0.6

# <-- Live Status Settings -->

# Channel ID for live status updates
LiveStatusChannelID = 1342510703386296483

# Update interval for live status (in seconds)
LiveStatusUpdateInterval = 10
