# 📦 Built-in modules
from typing import Dict
import pathlib
import os

# 📥 Custom modules
from Utils.Logger import Logger, logging, ConsoleHandler

# ⚙️ Settings
from Config import LogLevel, Intents, CommandPrefix

# 👾 Discord modules
from discord.ext import commands
import discord


# 🌱 Load environment variables from .env file
def LoadEnv() -> Dict[str, str]:
	EnvDict = {}
	try:
		with open('.env', 'r') as File:
			for Line in File:
				if '=' in Line:
					Key, Value = Line.strip().split('=', 1)
					EnvDict[Key] = Value
		return EnvDict
	except FileNotFoundError:
		# 🔄 Fallback to process environment when .env is missing
		Keys = ['DISCORD_BOT_TOKEN']
		for Key in Keys:
			Value = os.environ.get(Key)
			if Value:
				EnvDict[Key] = Value
		if not EnvDict:
			raise ValueError('No valid environment variables found.')
		return EnvDict


class Bot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def setup_hook(self) -> None:
		for Cog in pathlib.Path('Cogs').glob('*.py'):
			if Cog.name.startswith('_'):
				continue
			Logger.info(f'• Loading extension: Cogs.{Cog.stem}')
			await self.load_extension(f'Cogs.{Cog.stem}')
		await self.tree.sync()

	async def on_ready(self) -> None:
		if self.user:
			Logger.info(f'Logged in as {self.user.display_name} ({self.user.id})')
		else:
			Logger.error('Failed to get bot user details')
			return

	async def on_message(self, message: discord.Message) -> None:
		if message.author == self.user:
			return
		Channel = message.channel.name if isinstance(message.channel, discord.TextChannel) else 'DM'
		Logger.info(f'[#{Channel}] Message from {message.author.display_name}: {message.content}')
		await self.process_commands(message)


DiscordLogger = logging.getLogger('discord')
DiscordLogger.setLevel(LogLevel)
DiscordLogger.addHandler(ConsoleHandler)
DiscordLogger.propagate = False
logging.getLogger('discord.http').setLevel(LogLevel)

Env = LoadEnv()
Token = Env.get('DISCORD_BOT_TOKEN')

if Token is None:
	raise ValueError('DISCORD_BOT_TOKEN is not set in environment variables.')

Instance = Bot(intents=Intents, command_prefix=CommandPrefix)
Instance.run(
	Token,
	log_handler=None,
	log_level=LogLevel,
)
