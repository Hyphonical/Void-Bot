import discord
from discord.ext import commands
from discord import app_commands
from Utils.Logger import Logger

# === Role ID for Weekly Summary Notifications ===
WEEKLY_SUMMARY_ROLE_ID = 1427011632164376617


# === Cog definition ===
class PreferencesSystem(commands.Cog):
	"""
	🛠️ Preferences System Cog: Allows members to set personal preferences like weekly summary notifications.
	Modular and persistent with JSON.
	"""

	def __init__(self, bot):
		self.bot = bot

	# !preferences (Prefix)
	@commands.command(name='preferences')
	async def preferences_command(self, ctx):
		"""
		🛠️ Open your preferences menu.
		"""
		embed = self.get_preferences_help_embed(ctx, ctx.author)
		view = PreferencesView(ctx.author.id, ctx.guild, ctx.author)  # Pass user
		await ctx.send(embed=embed, view=view)

	# /preferences (Slash) - Global, since guild ID not set
	@app_commands.command(name='preferences', description='🛠️ Open your preferences menu.')
	async def preferences_slash(self, interaction: discord.Interaction):
		embed = self.get_preferences_help_embed(interaction, interaction.user)
		view = PreferencesView(
			interaction.user.id, interaction.guild, interaction.user
		)  # Pass user
		await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

	# 🧩 Shared Helper for preferences embed (used in prefix and slash)
	def get_preferences_help_embed(self, ctx_or_interaction, user):
		has_role = any(role.id == WEEKLY_SUMMARY_ROLE_ID for role in user.roles)
		status = '✅ Enabled' if has_role else '❌ Disabled'
		embed = discord.Embed(
			title='🛠️ Preferences Menu',
			description=f'Customize your experience. Weekly summary notifications are currently **{status}**.',
			# Removed color=PINK
		)
		embed.add_field(
			name='Options',
			value='🔔 Toggle Weekly Summary Notifications – Opt-in to receive role <@&1427011632164376617> for weekly updates.',
			inline=False,
		)
		# Removed set_pink_footer
		return embed


# === View for preferences menu ===
class PreferencesView(discord.ui.View):
	def __init__(self, user_id, guild, user):  # Add user parameter
		super().__init__(timeout=300)  # 5 minutes
		self.user_id = user_id
		self.guild = guild
		self.user = user  # Store user
		# Check current status using user.roles directly
		has_role = any(role.id == WEEKLY_SUMMARY_ROLE_ID for role in user.roles)
		label = (
			'Disable Weekly Summary Notifications'
			if has_role
			else 'Enable Weekly Summary Notifications'
		)
		emoji = '🔕' if has_role else '🔔'
		# Add the button with dynamic label
		self.add_item(ToggleWeeklySummaryButton(label, emoji, user_id, guild))


class ToggleWeeklySummaryButton(discord.ui.Button):
	def __init__(self, label, emoji, user_id, guild):
		super().__init__(label=label, style=discord.ButtonStyle.primary, emoji=emoji)
		self.user_id = user_id
		self.guild = guild

	async def callback(self, interaction: discord.Interaction):
		if interaction.user.id != self.user_id:
			await interaction.response.send_message('This menu is not for you.', ephemeral=True)
			return
		member = interaction.user  # Use interaction.user directly, as it's the member
		if not member:
			await interaction.response.send_message('Member not found.', ephemeral=True)
			return
		role = self.guild.get_role(WEEKLY_SUMMARY_ROLE_ID)
		if not role:
			await interaction.response.send_message(
				'Weekly summary role not found.', ephemeral=True
			)
			return
		if role in member.roles:
			await member.remove_roles(role)
			status = 'disabled'
		else:
			await member.add_roles(role)
			status = 'enabled'
		await interaction.response.send_message(
			f'Weekly summary notifications {status}.', ephemeral=True
		)
		Logger.info(f'User {interaction.user} toggled weekly summary role to {status}.')

		# Note: Since the message is ephemeral, we can't edit it. The status is shown in the button label and embed initially.


# === Setup function ===
async def setup(bot):
	"""
	Setup function to add the PreferencesSystem cog.
	"""
	await bot.add_cog(PreferencesSystem(bot))
