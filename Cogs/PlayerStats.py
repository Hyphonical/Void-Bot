# 📦 Built-in modules
import urllib.request
import urllib.parse
import http.cookiejar
import difflib
import gzip
import json
import os
from datetime import datetime

# ⚙️ Settings
from Config import FuzzyMatchingThreshold, BotName

# 👾 Discord modules
from discord.ext import commands
import discord


class PlayerStats(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot
		# 🍪 Cookie jar for auth
		self.CookieJar = http.cookiejar.CookieJar()
		self.Opener = urllib.request.build_opener(
			urllib.request.HTTPCookieProcessor(self.CookieJar)
		)

	# 🔐 Login to get auth cookie
	def Login(self) -> bool:
		User = os.environ.get('PLAN_USER')
		Password = os.environ.get('PLAN_PASSWORD')
		if not User or not Password:
			return False
		LoginUrl = 'https://plan.voidtales.win/auth/login'
		Data = urllib.parse.urlencode({'user': User, 'password': Password}).encode('utf-8')
		Req = urllib.request.Request(LoginUrl, data=Data, method='POST')
		Req.add_header('accept', 'application/json')
		Req.add_header('Content-Type', 'application/x-www-form-urlencoded')
		try:
			with self.Opener.open(Req) as Response:
				if Response.status == 200:
					ResponseData = json.loads(Response.read().decode('utf-8'))
					return ResponseData.get('success', False)
		except Exception:
			pass
		return False

	@commands.hybrid_command(
		name='playerstats',
		description='Get player statistics from Plan API',
		aliases=['stats', 'player', 'profile'],
	)
	async def PlayerStats(self, ctx: commands.Context, name: str | None = None) -> None:
		# 💡 If no name provided, use Discord display name
		if name is None:
			name = ctx.author.display_name

		# 🌐 Fetch environment variables
		ServerUUID = os.environ.get('PLAN_SERVER_UUID')
		if not ServerUUID:
			Embed = discord.Embed(
				title='Error',
				description='Environment variables are missing',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
			return

		# 🔐 Ensure login before API request
		if not self.Login():
			Embed = discord.Embed(
				title='Error',
				description='Authentication failed.',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
			return

		# 📡 Prepare API request
		Url = f'https://plan.voidtales.win/v1/playersTable?server={ServerUUID}'
		Req = urllib.request.Request(Url)
		Req.add_header('accept', 'application/json')

		Status = None
		try:
			# 🔍 Fetch data from API
			with self.Opener.open(Req) as Response:
				Status = Response.status
				if Status != 200:
					Embed = discord.Embed(
						title='Error',
						description=f'API request failed with status {Status}.',
						color=0xF5A3A3,
					)
					Embed.set_footer(text=BotName)
					await ctx.send(embed=Embed)
					return
				RawData = Response.read()
				if Response.headers.get('Content-Encoding') == 'gzip':
					RawData = gzip.decompress(RawData)
				DecodedData = RawData.decode('utf-8', errors='ignore')
				Data = json.loads(DecodedData)

			# 📊 Process and format player stats
			Players = Data.get('players', [])
			if not Players:
				Embed = discord.Embed(
					title='Error',
					description='No player data available.',
					color=0xF5A3A3,
				)
				Embed.set_footer(text=BotName)
				await ctx.send(embed=Embed)
				return

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
				Embed.set_footer(text=BotName)
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
		except Exception as E:
			Embed = discord.Embed(
				title='Error',
				description=f'Failed to fetch player stats for `{name}`: {E}',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(PlayerStats(Bot))
