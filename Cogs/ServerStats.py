# 📦 Built-in modules
import base64
import io
import socket
import time

# 📥 Custom modules
from Config import DefaultServer, DefaultServerPort
from Utils.Socket import GetStatus
from Utils.Plan import PlanAPI

# ⚙️ Settings
from Config import (
	BotName,
)

# 👾 Discord modules
from discord.ui import View, Button
from discord.ext import commands
import discord


# 💡 Strip Minecraft color codes (e.g., §a, §l)
def StripColorCodes(Text: str) -> str:
	Out = []
	_ = 0
	while _ < len(Text):
		if Text[_] == '§' and _ + 1 < len(Text):
			_ += 2
			continue
		Out.append(Text[_])
		_ += 1
	return ''.join(Out)


# 💡 Format the "description" field from status JSON
def FormatDescription(Desc) -> str:
	if isinstance(Desc, str):
		return StripColorCodes(Desc)
	if isinstance(Desc, dict):
		Text = Desc.get('text', '')
		Extra = Desc.get('extra', [])
		Parts = [Text] + [FormatDescription(E) for E in Extra]
		return StripColorCodes(''.join(Parts)).strip() or 'No description'
	return 'No description'


# 💡 Measure latency (ping) to the server
def MeasureLatency(Host: str, Port: int) -> float | None:
	try:
		StartTime = time.time()
		Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		Sock.settimeout(5)  # Timeout after 5 seconds
		Sock.connect((Host, Port))
		Sock.close()
		EndTime = time.time()
		return (EndTime - StartTime) * 1000  # Convert to milliseconds
	except Exception:
		return None


# 💡 Get emoji based on latency
def GetPingEmoji(Latency: float | None) -> str:
	if Latency is None:
		return '<:Ping0:1411342120253390878>'  # No connection
	elif Latency > 500:
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


# 💡 Get emoji based on change from 30d to 24h (increase/decrease)
def GetChangeEmoji(Current: str, Previous: str, IsIncreaseGood: bool = True) -> str:
	# 📊 Parse values to floats
	def ParseVal(Val: str) -> float | None:
		Val = Val.strip()
		if '%' in Val:
			return float(Val.replace('%', ''))
		if 'GB' in Val:
			return float(Val.replace('GB', ''))
		if 'h' in Val or 'm' in Val or 's' in Val:
			# Parse downtime: e.g., "20h 43m 34s" -> seconds
			Parts = Val.replace('h', ' ').replace('m', ' ').replace('s', '').split()
			Seconds = 0.0
			if len(Parts) >= 1:
				Seconds += float(Parts[0]) * 3600  # hours
			if len(Parts) >= 2:
				Seconds += float(Parts[1]) * 60  # minutes
			if len(Parts) >= 3:
				Seconds += float(Parts[2])  # seconds
			return Seconds
		try:
			return float(Val)
		except ValueError:
			return None

	CurrentVal = ParseVal(Current)
	PrevVal = ParseVal(Previous)
	if CurrentVal is None or PrevVal is None:
		return ''

	IsIncrease = CurrentVal > PrevVal
	if IsIncreaseGood:
		# For good metrics (e.g., TPS, players), increase is good, decrease is bad
		return (
			'<:GreenIncrease:1411407181802115214>'
			if IsIncrease
			else '<:RedDecrease:1411407212374392842>'
		)
	else:
		# For bad metrics (e.g., CPU, RAM, downtime), increase is bad, decrease is good
		return (
			'<:RedIncrease:1411409442502611005>'
			if IsIncrease
			else '<:GreenDecrease:1411409470315041009>'
		)


# 💡 Create status embed and file from server data
def CreateStatusEmbed(
	Status, Host: str, Port: int, BotName: str, PerfData: dict | None = None
) -> tuple[discord.Embed, discord.File | None]:
	# 📊 Format the response as an embed
	Version = Status.get('version', {}).get('name', 'Unknown')
	PlayersOnline = Status.get('players', {}).get('online', 0)
	PlayersMax = Status.get('players', {}).get('max', 0)
	Description = FormatDescription(Status.get('description', 'No description'))
	FaviconUrl = Status.get('favicon')

	# 📡 Measure latency
	Latency = MeasureLatency(Host, Port)
	PingEmoji = GetPingEmoji(Latency)
	LatencyText = f'{Latency:.0f}ms' if Latency is not None else 'Offline'

	Embed = discord.Embed(
		title=f'Minecraft Server Status for {Host}:{Port}',
		color=0xA0D6B4,
	)
	Embed.description = f"""
	Version: `{Version}` <:Version:1411439439342731334>
	Players: `{PlayersOnline}/{PlayersMax}` <:Player:1411439027508220043>
	Latency: `{LatencyText}` {PingEmoji}
	Description: ```{Description}```
	"""

	# 🖼️ Add server logo if available
	File = None
	if FaviconUrl and ',' in FaviconUrl:
		# Decode base64 and create file attachment
		Base64Data = FaviconUrl.split(',', 1)[1]
		ImageData = base64.b64decode(Base64Data)
		ImageBuffer = io.BytesIO(ImageData)
		ImageBuffer.seek(0)
		File = discord.File(ImageBuffer, 'favicon.png')
		Embed.set_thumbnail(url='attachment://favicon.png')
	Embed.set_footer(text=BotName)
	return Embed, File


class Minecraft(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot
		self.PlanAPI = PlanAPI()

	@commands.hybrid_command(
		name='mcstatus',
		description='Get Minecraft server status',
		aliases=['status', 'online', 'server'],
	)
	async def MCStatus(
		self, ctx: commands.Context, host: str | None = None, port: int = 25565
	) -> None:
		if host is None:
			host = DefaultServer
		if port == 25565 and host == DefaultServer:
			port = DefaultServerPort
		try:
			# 🌐 Fetch server status
			Status = GetStatus(host, port)
			# 📈 Fetch performance data
			ServerUUID = self.PlanAPI.Env.get('PLAN_SERVER_UUID')
			PerfData = self.PlanAPI.GetPerformanceOverview(ServerUUID) if ServerUUID else None
			Embed, File = CreateStatusEmbed(Status, host, port, BotName, PerfData)

			# 🔄 Create and attach the refresh view
			ViewInstance = RefreshView(host, port, BotName, self.PlanAPI)

			if File:
				await ctx.send(embed=Embed, file=File, view=ViewInstance)
			else:
				await ctx.send(embed=Embed, view=ViewInstance)
		except Exception:
			Embed = discord.Embed(
				title='Error',
				description='Failed to fetch server status',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)

	@commands.hybrid_command(
		name='mcperf',
		description='Get Minecraft server performance overview',
		aliases=['perf', 'performance'],
	)
	async def MCPerf(self, ctx: commands.Context) -> None:
		ServerUUID = self.PlanAPI.Env.get('PLAN_SERVER_UUID')
		if not ServerUUID:
			Embed = discord.Embed(
				title='Error',
				description='Environment variables are missing',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
			return
		PerfData = self.PlanAPI.GetPerformanceOverview(ServerUUID)
		if not PerfData or 'numbers' not in PerfData:
			Embed = discord.Embed(
				title='Error',
				description='Failed to fetch performance data',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
			return
		Numbers = PerfData['numbers']
		Embed = discord.Embed(
			title='Server Performance Overview',
			color=0xA0D6B4,
		)
		Embed.description = f"""
		TPS: `{Numbers.get('tps_24h', 'N/A')}` {GetChangeEmoji(Numbers.get('tps_24h', ''), Numbers.get('tps_30d', ''), True)}
		Downtime: `{Numbers.get('server_downtime_24h', 'N/A')}` {GetChangeEmoji(Numbers.get('server_downtime_24h', ''), Numbers.get('server_downtime_30d', ''), False)}
		CPU: `{Numbers.get('cpu_24h', 'N/A')}` {GetChangeEmoji(Numbers.get('cpu_24h', ''), Numbers.get('cpu_30d', ''), False)}
		RAM: `{Numbers.get('ram_24h', 'N/A')}` {GetChangeEmoji(Numbers.get('ram_24h', ''), Numbers.get('ram_30d', ''), False)}
		Entities: `{Numbers.get('entities_24h', 'N/A')}` {GetChangeEmoji(Numbers.get('entities_24h', ''), Numbers.get('entities_30d', ''), False)}
		Chunks: `{Numbers.get('chunks_24h', 'N/A')}` {GetChangeEmoji(Numbers.get('chunks_24h', ''), Numbers.get('chunks_30d', ''), False)}
		Players: `{Numbers.get('players_24h', 'N/A')}` {GetChangeEmoji(Numbers.get('players_24h', ''), Numbers.get('players_30d', ''), True)}
		"""
		Embed.set_footer(text=BotName)
		await ctx.send(embed=Embed)


class RefreshView(View):
	def __init__(self, Host: str, Port: int, BotName: str, PlanAPI: PlanAPI):
		super().__init__(timeout=None)
		self.Host = Host
		self.Port = Port
		self.BotName = BotName
		self.PlanAPI = PlanAPI

	@discord.ui.button(
		label='Refresh', style=discord.ButtonStyle.grey, emoji='<:Refresh:1411438460190986330>'
	)
	async def RefreshButton(self, interaction: discord.Interaction, button: Button):
		try:
			# 🌐 Re-fetch server status
			Status = GetStatus(self.Host, self.Port)
			# 📈 Re-fetch performance data
			ServerUUID = self.PlanAPI.Env.get('PLAN_SERVER_UUID')
			PerfData = self.PlanAPI.GetPerformanceOverview(ServerUUID) if ServerUUID else None
			Embed, File = CreateStatusEmbed(Status, self.Host, self.Port, self.BotName, PerfData)
			await interaction.response.edit_message(embed=Embed, view=self)
		except Exception:
			ErrorEmbed = discord.Embed(
				title='Error',
				description='Failed to fetch server status',
				color=0xF5A3A3,
			)
			ErrorEmbed.set_footer(text=self.BotName)
			await interaction.response.edit_message(embed=ErrorEmbed, view=self)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Minecraft(Bot))
