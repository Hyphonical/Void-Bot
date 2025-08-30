# 👾 Discord modules
from discord.ext import commands


# 💡 Helper function to format nanoseconds into readable units
def FormatNs(Ns: int) -> str:
	Ms = Ns // 1_000_000
	Us = (Ns % 1_000_000) // 1_000
	NsRem = Ns % 1_000
	Parts = []
	if Ms > 0:
		Parts.append(f'{Ms}ms')
	if Us > 0 or Ms > 0:
		Parts.append(f'{Us}µs')
	Parts.append(f'{NsRem}ns')
	return ' '.join(Parts)


class Ping(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(
		name='ping', aliases=['latency'], description="Check the bot's latency"
	)
	async def ping(self, ctx: commands.Context) -> None:
		await ctx.send(f'`Latency: {self.Bot.latency * 1000:.2f}ms`')


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Ping(Bot))
