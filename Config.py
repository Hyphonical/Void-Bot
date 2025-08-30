# 📦 Built-in modules
import logging

# 👾 Discord modules
import discord

# <-- Logging Settings -->

# Global Log Level
LogLevel = logging.INFO

# <-- Discord Settings -->

# Discord Intents
Intents = discord.Intents.default()
Intents.message_content = True

# Command Prefix
CommandPrefix = '!'

# <-- Minecraft Settings -->

Presence = discord.Game(name='Void Tales')
ProtocolVersion = 766  # 1.20.5
DefaultServer = 'play.voidtales.win'
DefaultServerPort = 25565
PresenceUpdateInterval = 30
