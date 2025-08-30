# 📥 Custom modules
from Utils.Plan import PlanAPI

# ⚙️ Settings
from Config import BotName

# 👾 Discord modules
from discord.ext import commands
import discord


class Leaderboard(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot
		self.PlanAPI = PlanAPI()

	@commands.hybrid_command(
		name='leaderboard',
		description='Get top 10 most active players leaderboard',
		aliases=['lb', 'top'],
	)
	async def Leaderboard(self, ctx: commands.Context) -> None:
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

		# 📊 Fetch all player data
		Data = self.PlanAPI.GetPlayerStats(ServerUUID)
		if not Data or 'players' not in Data:
			Embed = discord.Embed(
				title='Error',
				description='Failed to fetch player data.',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
			return

		Players = Data['players']
		if not Players:
			Embed = discord.Embed(
				title='Error',
				description='No players found.',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
			return

		# 🏆 Sort players by activity index descending
		SortedPlayers = sorted(Players, key=lambda P: P.get('activityIndex', 0), reverse=True)

		# 📈 Get top 10 and normalize activity index to percentage
		TopPlayers = SortedPlayers[:10]
		LeaderboardText = ''
		for i, Player in enumerate(TopPlayers, start=1):
			Name = Player.get('playerName', 'Unknown')
			ActivityIndex = Player.get('activityIndex', 0)
			Percentage = round((ActivityIndex / 5) * 100, 2) if ActivityIndex else 0
			LeaderboardText += f'{i}. {Name}: `{Percentage}%`\n'

		# 🎨 Create embed
		Embed = discord.Embed(
			title='Top 10 Most Active Players',
			description=LeaderboardText,
			color=0xA0D6B4,
		)
		Embed.set_footer(text=BotName)
		await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Leaderboard(Bot))
