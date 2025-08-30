# ⚙️ Settings
from Config import (
	PresenceUpdateInterval,
	DefaultServer,
	DefaultServerPort,
)

# 📥 Custom modules
from Utils.Socket import GetStatus

# 👾 Discord modules
from discord.ext import commands, tasks
import discord


class Presence(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	@tasks.loop(seconds=PresenceUpdateInterval)
	async def update_presence(self):
		Status = GetStatus(DefaultServer, DefaultServerPort)
		PlayersOnline = Status.get('players', {}).get('online', 0)
		await self.bot.change_presence(
			status=discord.Status.idle if PlayersOnline == 0 else discord.Status.online,
			activity=discord.Game(
				name=f'Void Tales | {PlayersOnline} players',
			),
		)

	@commands.Cog.listener()
	async def on_ready(self):
		self.update_presence.start()


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Presence(bot))
