# 📦 Built-in modules
import difflib
import pathlib
import time

# 📥 Custom modules
from Utils.Logger import Logger, logging, ConsoleHandler
from Utils.Env import LoadEnv

# ⚙️ Settings
from Config import (
	LogLevel,
	Intents,
	CommandPrefix,
	BlacklistedChannels,
	BotName,
	FuzzyMatchingThreshold,
	MessageCooldown,
)

# 👾 Discord modules
from discord.ext import commands
import discord


class Bot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.remove_command('help')
		# ⏱️ Track user cooldowns (user ID -> last message timestamp)
		self.UserCooldowns = {}

	async def setup_hook(self) -> None:
		for Cog in pathlib.Path('Cogs').glob('*.py'):
			if Cog.name.startswith('_'):
				continue
			Logger.info(f'• Loading extension: {Cog.stem}')
			await self.load_extension(f'Cogs.{Cog.stem}')
		Logger.info('• Syncing application commands...')
		await self.tree.sync()
		Logger.info('• Done loading Cogs.')

	async def on_ready(self) -> None:
		if self.user:
			Logger.info(f'Logged in as {self.user.display_name} ({self.user.id})')
		else:
			Logger.error('Failed to get bot user details')
			return

	async def on_message(self, message: discord.Message) -> None:
		if message.author == self.user:
			return
		# 🚫 Skip logging if channel is blacklisted
		if (
			isinstance(message.channel, discord.TextChannel)
			and message.channel.id in BlacklistedChannels
		):
			return
		Channel = message.channel.name if isinstance(message.channel, discord.TextChannel) else 'DM'
		Logger.info(f'[#{Channel}] Message from {message.author.display_name}: {message.content}')

		# ⏱️ Check message cooldown
		UserId = message.author.id
		CurrentTime = time.time()
		LastMessageTime = self.UserCooldowns.get(UserId, 0)
		if CurrentTime - LastMessageTime < MessageCooldown:
			# 📤 Send cooldown embed
			RemainingTime = int(MessageCooldown - (CurrentTime - LastMessageTime))
			Embed = discord.Embed(
				title='Cooldown Active',
				description=f'Please wait `{RemainingTime}` seconds before sending another message.',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await message.channel.send(embed=Embed, delete_after=20)
			return
		# 🔄 Update cooldown timestamp
		self.UserCooldowns[UserId] = CurrentTime

		await self.process_commands(message)

	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.CommandNotFound):
			# 🔍 Fuzzy search for similar commands
			InvokedCommand = ctx.invoked_with
			AllCommands = [Cmd.name for Cmd in self.commands]
			AllCommands.extend([Alias for Cmd in self.commands for Alias in Cmd.aliases])
			CloseMatches = difflib.get_close_matches(
				InvokedCommand, AllCommands, n=1, cutoff=FuzzyMatchingThreshold
			)
			if CloseMatches:
				SuggestedCommand = CloseMatches[0]
				Embed = discord.Embed(
					title='Command Not Found',
					description=f'Did you mean `{CommandPrefix}{SuggestedCommand}`? The command `{CommandPrefix}{InvokedCommand}` is not recognized.',
					color=0xF5A3A3,
				)
				Embed.set_footer(text=BotName)
				await ctx.send(embed=Embed)
			else:
				Embed = discord.Embed(
					title='Command Not Found',
					description=f'The command `{CommandPrefix}{InvokedCommand}` is not recognized.',
					color=0xF5A3A3,
				)
				Embed.set_footer(text=BotName)
				await ctx.send(embed=Embed)
		elif isinstance(error, commands.MissingPermissions):
				Embed = discord.Embed(
					title='Missing Permissions',
					description=f'You do not have permission to use the command `{CommandPrefix}{ctx.invoked_with}`.',
					color=0xF5A3A3,
				)
				Embed.set_footer(text=BotName)
				await ctx.send(embed=Embed)
		elif isinstance(error, commands.BadArgument):
			Embed = discord.Embed(
				title='Bad Argument',
				description=f'Invalid argument provided for command `{CommandPrefix}{ctx.invoked_with}`.',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
		else:
			# 🔄 Re-raise other errors for default handling
			Logger.error(f'Unhandled error: {error}')
			raise error

	async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
		# ✏️ Log message edits
		if before.content != after.content:
			# 🚫 Skip logging if channel is blacklisted
			if (
				isinstance(before.channel, discord.TextChannel)
				and before.channel.id in BlacklistedChannels
			):
				return
			Channel = (
				before.channel.name if isinstance(before.channel, discord.TextChannel) else 'DM'
			)
			Logger.info(
				f'[#{Channel}] Message edited by {before.author.display_name}: "{before.content}" -> "{after.content}"'
			)

	async def on_message_delete(self, message: discord.Message) -> None:
		# 🗑️ Log message deletions
		# 🚫 Skip logging if channel is blacklisted
		if (
			isinstance(message.channel, discord.TextChannel)
			and message.channel.id in BlacklistedChannels
		):
			return
		Channel = message.channel.name if isinstance(message.channel, discord.TextChannel) else 'DM'
		Logger.info(
			f'[#{Channel}] Message deleted by {message.author.display_name}: "{message.content}"'
		)


DiscordLogger = logging.getLogger('discord')
DiscordLogger.setLevel(LogLevel)
DiscordLogger.addHandler(ConsoleHandler)
DiscordLogger.propagate = False
logging.getLogger('discord.http').setLevel(LogLevel)

Env = LoadEnv()
Token = Env.get('DISCORD_BOT_TOKEN') if Env else None
if not Token:
	Logger.error('Error: Discord bot token not found in environment variables.')
	exit(1)

Instance = Bot(intents=Intents, command_prefix=CommandPrefix)
Instance.run(
	Token,
	log_handler=None,
	log_level=LogLevel,
)
