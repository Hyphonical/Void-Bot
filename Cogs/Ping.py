# ⚙️ Settings
from Config import (
	BotName,
)

# 👾 Discord modules
from discord.ext import commands
import discord


# 💡 Get emoji based on latency
def GetPingEmoji(Latency: float) -> str:
	if Latency > 500:
		return '<:Ping1:1411342192647082045>'  # Extremely high
	elif Latency > 400:
		return '<:Ping2:1411342222489550940>'
	elif Latency > 300:
		return '<:Ping3:1411342248628588595>'
	elif Latency > 200:
		return '<:Ping4:1411342274423558275>'
	elif Latency > 100:
		return '<:Ping5:1411342297856999424>'
	else:
		return '<:Ping6:1411342320955031664>'  # Low ping


class Ping(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(
		name='ping', aliases=['latency'], description="Check the bot's latency"
	)
	async def Ping(self, ctx: commands.Context) -> None:
		Embed = discord.Embed(
			title='Latency',
			description=f'`{self.Bot.latency * 1000:.2f}ms` {GetPingEmoji(self.Bot.latency * 1000)}',
			color=0xA0D6B4,
		)
		Embed.set_footer(text=BotName)
		await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Ping(Bot))
