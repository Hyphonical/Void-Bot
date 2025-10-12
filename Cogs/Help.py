# ⚙️ Settings
from Config import (
	CommandPrefix,
	BotName,
)

# 👾 Discord modules
from discord.ext import commands
import discord


class Help(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(
		name='help',
		aliases=['commands'],
		description='Shows help for commands or categories.',
	)
	async def Help(self, Ctx: commands.Context) -> None:
		# 📋 Build dynamic help embed with categories
		Embed = discord.Embed(
			title='Bot Commands',
			timestamp=discord.utils.utcnow(),
			color=0xA0D6B4,
		)
		Embed.set_footer(text=BotName)

		# 🗂️ Group commands by cog
		Categories = {}
		for Command in self.Bot.commands:
			# Skip hidden commands like 'say'
			if Command.name in ['say']:
				continue
			CogName = Command.cog.qualified_name if Command.cog else 'No Category'
			if CogName not in Categories:
				Categories[CogName] = []
			CommandList = [f'`{CommandPrefix}{Command.name}`']
			if Command.aliases:
				CommandList.extend([f'`{CommandPrefix}{Alias}`' for Alias in Command.aliases])
			Categories[CogName].append(' | '.join(CommandList))

		# ➕ Add fields for each category
		for Category, Commands in Categories.items():
			Embed.add_field(
				name=Category,
				value='\n'.join(Commands),
				inline=False,
			)

		await Ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Help(Bot))
