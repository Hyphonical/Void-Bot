# 📦 Built-in modules
import difflib
import json

# 📥 Custom modules
from Utils.Plan import PlanAPI

# ⚙️ Settings
from Config import FuzzyMatchingThreshold, BotName

# 👾 Discord modules
from discord.ext import commands
import discord


# 💡 Get emoji based on latency
def GetPingEmoji(Latency: float) -> str:
	if Latency > 500:
		return '<:Ping1:1422932999401639937>'  # Extremely high
	elif Latency > 400:
		return '<:Ping2:1422933063759036578>'
	elif Latency > 300:
		return '<:Ping3:1422933085212770324>'
	elif Latency > 200:
		return '<:Ping4:1422933101138546688>'
	elif Latency > 100:
		return '<:Ping5:1422933118930780291>'
	else:
		return '<:Ping6:1422933134407897119>'  # Low ping


class PlayerStats(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot
		self.PlanAPI = PlanAPI()

	@commands.hybrid_command(
		name='playerstats',
		description='Get player statistics from Plan API',
		aliases=['stats', 'player', 'profile', 'statistics', 'p'],
	)
	async def PlayerStats(self, ctx: commands.Context, name: str | None = None) -> None:
		# 💡 If no name provided, use Discord display name
		if name is None:
			name = ctx.author.display_name

		# 🌐 Fetch environment variables
		ServerUUID = self.PlanAPI.Env.get('PLAN_SERVER_UUID')
		if not ServerUUID:
			Embed = discord.Embed(
				title='Error',
				timestamp=discord.utils.utcnow(),
				description='Environment variables are missing',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
			return

		# 📊 Fetch player data
		Player = self.PlanAPI.GetPlayerStats(ServerUUID, name)
		if not Player:
			Embed = discord.Embed(
				title='Error',
				timestamp=discord.utils.utcnow(),
				description=f'No data found for `{name}`.',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
			return

		# 🕒 Helper to convert milliseconds to d h m s format
		def ConvertMsToDhms(Milliseconds):
			Seconds = Milliseconds // 1000
			Days = Seconds // 86400
			Hours = (Seconds % 86400) // 3600
			Minutes = (Seconds % 3600) // 60
			Secs = Seconds % 60
			return f'{Days}d {Hours}h {Minutes}m {Secs}s'

		# 📈 Extract data
		Playtime = ConvertMsToDhms(Player.get('playtimeActive', 0))
		Sessions = Player.get('sessionCount', 0)
		Country = Player.get('country', 'Unknown')
		PingAvg = Player.get('pingAverage', 'N/A')
		Balance = Player.get('extensionValues', {}).get('balance', {}).get('value', '0')
		Group = (
			Player.get('extensionValues', {})
			.get('primaryGroup', {})
			.get('value', 'None')
			.capitalize()
		)

		# 🏳️ Include country flag from Utils/Countries.json
		with open('Utils/Countries.json', 'r', encoding='utf-8') as f:
			Countries = json.load(f)
		CountryFlag = difflib.get_close_matches(
			Country, Countries.keys(), n=1, cutoff=FuzzyMatchingThreshold
		)
		CountryFlag = Countries.get(CountryFlag[0], '') if CountryFlag else ''

		# 🎨 Create detailed embed
		Embed = discord.Embed(
			title=f'Player Stats: {Player.get("playerName", name)}',
			timestamp=discord.utils.utcnow(),
			color=0xA0D6B4,
		)
		Embed.description = f"""
		Playtime: `{Playtime}` <:Time:1422932510102523924>
		Sessions: `{Sessions}` <:Sessions:1422932457283391589>
		Country: `{Country}` {CountryFlag if CountryFlag else ''}
		Avg Ping: `{PingAvg}ms` {GetPingEmoji(PingAvg)}
		Balance: `{Balance}` <:Balance:1422932656517283941>
		Rank: `{Group}` <:Winner:1422932500061356193>
		"""
		Embed.set_thumbnail(
			url=f'https://api.mineatar.io/head/{Player.get("playerUUID")}?scale=10&overlay=true'
		)
		Embed.set_footer(text=BotName)
		await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(PlayerStats(Bot))
