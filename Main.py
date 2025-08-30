# 📦 Built-in modules
from typing import Dict
import pathlib
import os

# 📥 Custom modules
from Utils.Logger import Logger, logging, ConsoleHandler
from Utils.Socket import GetStatus

# ⚙️ Settings
from Config import (
	LogLevel,
	Intents,
	CommandPrefix,
	Presence,
	DefaultServer,
	DefaultServerPort,
	PresenceUpdateInterval,
)

# 👾 Discord modules
from discord.ext import commands, tasks
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
		Logger.info('• Syncing application commands...')
		await self.tree.sync()
		Logger.info('• Done loading Cogs.')

	async def on_ready(self) -> None:
		if self.user:
			Logger.info(f'Logged in as {self.user.display_name} ({self.user.id})')
			await self.change_presence(activity=Presence)
			self.UpdatePresence.start()
		else:
			Logger.error('Failed to get bot user details')
			return

	# 🔄 Task to update presence with server stats
	@tasks.loop(seconds=PresenceUpdateInterval)
	async def UpdatePresence(self):
		try:
			Status = GetStatus(DefaultServer, DefaultServerPort)
			PlayersOnline = Status.get('players', {}).get('online', 0)
			await self.change_presence(
				activity=discord.Game(name=f'Void Tales | {PlayersOnline} players')
			)
		except Exception as E:
			Logger.warning(f'Failed to update presence: {str(E)}')
			await self.change_presence(activity=Presence)  # Fallback to default

	async def on_message(self, message: discord.Message) -> None:
		if message.author == self.user:
			return
		Channel = message.channel.name if isinstance(message.channel, discord.TextChannel) else 'DM'
		Logger.info(f'[#{Channel}] Message from {message.author.display_name}: {message.content}')
		await self.process_commands(message)

	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.CommandNotFound):
			Embed = discord.Embed(
				title='Command Not Found',
				description=f'The command `{ctx.invoked_with}` is not recognized.',
				color=0xFF0000,
			)
			await ctx.send(embed=Embed)
		elif isinstance(error, commands.MissingPermissions):
			await ctx.send('You do not have permission to use this command.')
		elif isinstance(error, commands.BadArgument):
			await ctx.send('Invalid argument provided.')
		else:
			# 🔄 Re-raise other errors for default handling
			Logger.error(f'Unhandled error: {error}')
			raise error

	async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
		# ✏️ Log message edits
		if before.content != after.content:
			Channel = (
				before.channel.name if isinstance(before.channel, discord.TextChannel) else 'DM'
			)
			Logger.info(
				f'Message edited in #{Channel} by {before.author.display_name}: "{before.content}" -> "{after.content}"'
			)

	async def on_message_delete(self, message: discord.Message) -> None:
		# 🗑️ Log message deletions
		Channel = message.channel.name if isinstance(message.channel, discord.TextChannel) else 'DM'
		Logger.info(
			f'Message deleted in #{Channel} by {message.author.display_name}: "{message.content}"'
		)


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
