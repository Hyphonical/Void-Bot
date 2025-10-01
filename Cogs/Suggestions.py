# 📦 Built-in modules
import datetime

# 📥 Custom modules
from Config import SuggestionChannelID

# 👾 Discord modules
from discord.ext import commands
import discord


class Suggestions(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(
		name='suggest',
		description='Submit a suggestion as a poll',
		aliases=['suggestion', 'poll'],
	)
	async def suggest(self, ctx: commands.Context, *, suggestion: str) -> None:
		# 🚫 Check if suggestion is provided
		if not suggestion.strip():
			await ctx.send('Please provide a suggestion text.', ephemeral=True)
			return

		# 📤 Get the target channel
		Channel = self.Bot.get_channel(SuggestionChannelID)
		if not Channel or not isinstance(Channel, discord.TextChannel):
			await ctx.send('Suggestion channel not found or invalid.', ephemeral=True)
			return

		# 📊 Create poll with suggestion as question
		Poll = discord.Poll(question=suggestion, duration=datetime.timedelta(days=7))
		Poll.add_answer(text='Upvote', emoji='<:GreenIncrease:1422935980817645648>')
		Poll.add_answer(text='Unsure', emoji='<:Unknown:1422932441525653675>')
		Poll.add_answer(text='Downvote', emoji='<:RedDecrease:1422932924474331266>')

		# 📤 Send poll
		await Channel.send(
			content=f'Suggestion by {ctx.author.mention}',
			silent=True,
			poll=Poll,
		)
		await ctx.send('Suggestion poll created!', ephemeral=True)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Suggestions(Bot))
