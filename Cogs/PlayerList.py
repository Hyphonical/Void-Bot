# 📦 Built-in modules
import discord

# 📥 Custom modules
from Config import DefaultServer, DefaultServerPort
from Utils.Socket import GetStatus

# ⚙️ Settings
from Config import (
	BotName,
)

# 👾 Discord modules
from discord.ext import commands


class Players(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(
		name='playerlist',
		description='List online players on the Minecraft server',
		aliases=['players', 'list'],
	)
	async def PlayerList(
		self, ctx: commands.Context, host: str | None = None, port: int = 25565
	) -> None:
		if host is None:
			host = DefaultServer
		if port == 25565 and host == DefaultServer:
			port = DefaultServerPort
		try:
			# 🌐 Fetch server status
			Status = GetStatus(host, port)
			PlayersOnline = Status.get('players', {}).get('online', 0)
			PlayerSample = Status.get('players', {}).get('sample', [])

			if PlayersOnline == 0:
				# ❌ Fail embed for no players
				Embed = discord.Embed(
					title='No Players Online',
					description='There is currently no one online.',
					color=0xF5A3A3,
				)
				Embed.set_footer(text=BotName)
				await ctx.send(embed=Embed)
			else:
				# 📋 List players embed
				PlayerNames = [Player.get('name', 'Unknown') for Player in PlayerSample]
				PlayerList = (
					'\n'.join(PlayerNames) if PlayerNames else 'No player details available'
				)
				Embed = discord.Embed(
					title=f'Online Players ({PlayersOnline})',
					description=PlayerList,
					color=0xA0D6B4,
				)
				Embed.set_footer(text=BotName)
				await ctx.send(embed=Embed)
		except Exception:
			Embed = discord.Embed(
				title='Error',
				description='Failed to fetch player list',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Players(Bot))
