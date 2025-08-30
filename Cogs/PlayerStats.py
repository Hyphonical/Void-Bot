# 📦 Built-in modules
from datetime import datetime
import json
import difflib

# 📥 Custom modules
from Utils.Plan import PlanAPI

# ⚙️ Settings
from Config import FuzzyMatchingThreshold, BotName

# 👾 Discord modules
from discord.ext import commands
import discord


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
			timestamp=datetime.now(),
			color=0xA0D6B4,
		)
		Embed.description = f"""
		Playtime: `{Playtime}`
		Sessions: `{Sessions}`
		Country: `{Country}` {CountryFlag if CountryFlag else ''}
		Avg Ping: `{PingAvg} ms`
		Balance: `{Balance} $`
		Primary Group: `{Group}`
		"""
		Embed.set_thumbnail(url=f'https://api.mineatar.io/head/{Player.get("playerUUID")}?scale=16')
		Embed.set_footer(text=BotName)
		await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(PlayerStats(Bot))
