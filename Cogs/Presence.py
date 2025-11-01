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
import asyncio
import logging

# Use Presence logger
logger = logging.getLogger('Cogs.Presence')


class Presence(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@tasks.loop(seconds=PresenceUpdateInterval)
	async def update_presence(self):
		max_retries = 3
		for attempt in range(max_retries):
			try:
				Status = GetStatus(DefaultServer, DefaultServerPort)
				PlayersOnline = Status.get('players', {}).get('online', 0)
				await self.Bot.change_presence(
					status=discord.Status.idle if PlayersOnline == 0 else discord.Status.online,
					activity=discord.Game(
						name=f'Void Tales | {PlayersOnline} players',
					),
				)
				break  # Success, exit retry loop
			except Exception as e:
				logger.warning(f'Presence update attempt {attempt + 1}/{max_retries} failed: {e}')
				if attempt == max_retries - 1:
					# Fallback: Set to offline status after all retries failed
					try:
						await self.Bot.change_presence(
							status=discord.Status.dnd,
							activity=discord.Game('Void Tales | Server status unavailable'),
						)
						logger.info('Presence set to offline status due to server unavailability')
					except Exception as fallback_error:
						logger.error(f'Failed to set fallback presence: {fallback_error}')
				else:
					# Brief pause before retry
					await asyncio.sleep(1)

	@commands.Cog.listener()
	async def on_ready(self):
		self.update_presence.start()


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Presence(Bot))
