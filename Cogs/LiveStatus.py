# 📦 Built-in modules
import discord

# 📥 Custom modules
from Cogs.ServerStats import CreateStatusEmbed
from Config import (
	BotName,
	DefaultServer,
	DefaultServerPort,
	LiveStatusChannelID,
	LiveStatusUpdateInterval,
)
from Utils.Plan import PlanAPI
from Utils.Socket import GetStatus

# 👾 Discord modules
from discord.ext import commands, tasks
from discord.ui import View, Button


class LiveStatusView(View):
	def __init__(self, CogInstance):
		super().__init__(timeout=None)
		self.CogInstance = CogInstance

	@discord.ui.button(
		label='Refresh',
		style=discord.ButtonStyle.grey,
		emoji='<:Refresh:1422932521049657457>',
	)
	async def RefreshButton(self, Interaction: discord.Interaction, Button: Button):
		await self.CogInstance.UpdateStatusMessage(Interaction)


class LiveStatus(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot
		self.PlanAPI = PlanAPI()
		self.StatusMessage = None
		self.Channel = None

	@commands.Cog.listener()
	async def on_ready(self):
		# 🧹 Purge all messages in the live status channel on startup
		self.Channel = self.Bot.get_channel(LiveStatusChannelID)
		# 🏷️ Only purge if channel is a TextChannel
		if self.Channel and isinstance(self.Channel, discord.TextChannel):
			await self.Channel.purge()
			# 📤 Send initial embed
			await self.UpdateStatusMessage()
		elif self.Channel:
			# 📤 Send initial embed (no purge for non-text channels)
			await self.UpdateStatusMessage()
		# 🔄 Start the update loop
		self.UpdateStatusLoop.start()

	@tasks.loop(seconds=LiveStatusUpdateInterval)
	async def UpdateStatusLoop(self):
		if self.Channel and self.StatusMessage:
			await self.UpdateStatusMessage()

	async def UpdateStatusMessage(self, Interaction=None):
		try:
			# 🌐 Fetch server status
			Status = GetStatus(DefaultServer, DefaultServerPort)
			# 📈 Fetch performance data
			ServerUUID = self.PlanAPI.Env.get('PLAN_SERVER_UUID')
			PerfData = self.PlanAPI.GetPerformanceOverview(ServerUUID) if ServerUUID else None
			Embed, File = CreateStatusEmbed(
				Status, DefaultServer, DefaultServerPort, BotName, PerfData
			)

			ViewInstance = LiveStatusView(self)

			if self.StatusMessage:
				# ✏️ Edit existing message
				if File:
					await self.StatusMessage.edit(
						embed=Embed, attachments=[File], view=ViewInstance
					)
				else:
					await self.StatusMessage.edit(embed=Embed, view=ViewInstance)
			else:
				# 📤 Send new message
				if isinstance(self.Channel, discord.TextChannel):
					if File:
						self.StatusMessage = await self.Channel.send(
							embed=Embed, file=File, view=ViewInstance, silent=True
						)
					else:
						self.StatusMessage = await self.Channel.send(
							embed=Embed, view=ViewInstance, silent=True
						)
				else:
					# 🚫 Channel type does not support sending messages
					self.StatusMessage = None

			if Interaction:
				await Interaction.response.defer()
		except Exception:
			if Interaction:
				await Interaction.response.send_message('Failed to refresh status.', ephemeral=True)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(LiveStatus(Bot))
