# ⚙️ Settings
from Config import (
	BotName,
)

# 👾 Discord modules
from discord.ext import commands
import discord


class Ping(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(
		name='ping', aliases=['latency'], description="Check the bot's latency"
	)
	async def Ping(self, ctx: commands.Context) -> None:
		Embed = discord.Embed(
			title='Latency',
			description=f'`{self.Bot.latency * 1000:.2f}ms`',
			color=0xA0D6B4,
		)
		Embed.set_footer(text=BotName)
		await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Ping(Bot))
