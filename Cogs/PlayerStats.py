# 📦 Built-in modules
import urllib.request
import difflib
import gzip
import json
import os
from datetime import datetime

# 👾 Discord modules
from discord.ext import commands
import discord

# ⚙️ Settings
from Config import FuzzyMatchingThreshold, BotName


class PlayerStats(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(
		name='playerstats',
		description='Get player statistics from Plan API',
		aliases=['stats', 'player', 'profile'],
	)
	async def PlayerStats(self, ctx: commands.Context, name: str | None = None) -> None:
		# 🌐 Fetch environment variables
		Auth = os.environ.get('PLAN_AUTH')
		ServerUUID = os.environ.get('PLAN_SERVER_UUID')
		if not Auth or not ServerUUID:
			Embed = discord.Embed(
				title='Error',
				description='Environment variables are missing',
				color=0xF5A3A3,
			)
			await ctx.send(embed=Embed)
			return

		# 📡 Prepare API request
		Url = f'https://plan.voidtales.win/v1/playersTable?server={ServerUUID}'
		Req = urllib.request.Request(Url)
		Req.add_header('Cookie', f'auth={Auth}')

		try:
			# 🔍 Fetch data from API
			with urllib.request.urlopen(Req) as Response:
				RawData = Response.read()
				if Response.headers.get('Content-Encoding') == 'gzip':
					RawData = gzip.decompress(RawData)
				Data = json.loads(RawData.decode('utf-8'))

			# 📊 Process and format player stats
			Players = Data.get('players', [])
			if not Players:
				Embed = discord.Embed(
					title='Error',
					description='No player data available.',
					color=0xF5A3A3,
				)
				await ctx.send(embed=Embed)
				return

			# 💡 If no name provided, use Discord display name
			if name is None:
				name = ctx.author.display_name

			# 🔍 Fuzzy search for player
			PlayerNames = [P.get('playerName', '') for P in Players]
			Matches = difflib.get_close_matches(
				name, PlayerNames, n=1, cutoff=FuzzyMatchingThreshold
			)
			if not Matches:
				Embed = discord.Embed(
					title='Error',
					description=f'No close match found for `{name}`.',
					color=0xF5A3A3,
				)
				await ctx.send(embed=Embed)
				return
			MatchedName = Matches[0]
			Player = next((P for P in Players if P.get('playerName') == MatchedName), None)
			if not Player:
				Embed = discord.Embed(
					title='Error',
					description=f'Player `{MatchedName}` not found.',
					color=0xF5A3A3,
				)
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

			# 📈 Extract additional data
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
				title=f'Player Stats: {MatchedName}',
				timestamp=datetime.now(),
				color=0xA0D6B4,
			)
			Embed.description = f"""Playtime: {Playtime}
			Sessions: `{Sessions}`
			Country: `{Country}` {CountryFlag if CountryFlag else ''}
			Avg Ping: `{PingAvg} ms`
			Balance: `{Balance} $`
			Primary Group: `{Group}`
			"""
			Embed.set_thumbnail(
				url=f'https://api.mineatar.io/head/{Player.get("playerUUID")}?scale=16'
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
		except Exception:
			Embed = discord.Embed(
				title='Error',
				description=f'Failed to fetch player stats for `{name}`',
				color=0xF5A3A3,
			)
			await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(PlayerStats(Bot))
