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
	async def Suggest(self, Ctx: commands.Context, *, Suggestion: str) -> None:
		# 🚫 Check if suggestion is provided
		if not Suggestion.strip():
			await Ctx.send('Please provide a suggestion text.', ephemeral=True)
			return

		# 📤 Get the target channel
		Channel = self.Bot.get_channel(SuggestionChannelID)
		if not Channel or not isinstance(Channel, discord.TextChannel):
			await Ctx.send('Suggestion channel not found or invalid.', ephemeral=True)
			return

		# 📊 Create poll with suggestion as question
		Poll = discord.Poll(question=Suggestion, duration=datetime.timedelta(days=7))
		Poll.add_answer(text='Upvote', emoji='<:GreenIncrease:1411407181802115214>')
		Poll.add_answer(text='Unsure', emoji='<:Unknown:1411613426534322226>')
		Poll.add_answer(text='Downvote', emoji='<:RedDecrease:1411407212374392842>')

		# 📤 Send poll
		await Channel.send(
			content=f'Suggestion by {Ctx.author.mention}',
			silent=True,
			poll=Poll,
		)
		await Ctx.send('Suggestion poll created!', ephemeral=True)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Suggestions(Bot))
