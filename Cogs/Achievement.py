# 📦 Built-in modules
from pathlib import Path
import tempfile
import os

# 📥 Custom modules
from Utils.Achievement import MakeAchievement
import discord
from discord.ext import commands

# ⚙️ Settings
from Config import BotName


class Achievement(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(
		name='achievement',
		description='Generate a Minecraft-style achievement image',
		aliases=['ach', 'achiev'],
	)
	async def AchievementCommand(
		self, ctx: commands.Context, achievement: str, description: str, icon: str | None = None
	) -> None:
		# 🌱 Set default icon if none provided
		if icon is None:
			icon = 'Compass'

		try:
			# 🌱 Generate the achievement image
			BaseImgPath = Path('Utils/Input.png')
			Colors = [(255, 215, 0), (255, 255, 255)]  # Default gold and white
			with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as TmpFile:
				OutputPath = Path(TmpFile.name)
			MakeAchievement(BaseImgPath, icon, achievement, description, Colors, OutputPath)

			# 📤 Create embed with image
			Embed = discord.Embed(
				timestamp=discord.utils.utcnow(),
				color=0xA0D6B4,
			)
			Embed.set_image(url='attachment://achievement.png')
			Embed.set_footer(text=BotName)

			# 📤 Send embed with attached image
			await ctx.send(embed=Embed, file=discord.File(OutputPath, 'achievement.png'))

			# 🧹 Clean up temp file
			os.unlink(OutputPath)
		except ValueError as E:
			# ❌ Handle errors (e.g., invalid icon or text too long)
			Embed = discord.Embed(
				title='Error',
				timestamp=discord.utils.utcnow(),
				description=str(E),
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)
		except Exception:
			# ❌ Handle other errors
			Embed = discord.Embed(
				title='Error',
				timestamp=discord.utils.utcnow(),
				description='Failed to generate achievement image.',
				color=0xF5A3A3,
			)
			Embed.set_footer(text=BotName)
			await ctx.send(embed=Embed)


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Achievement(Bot))
