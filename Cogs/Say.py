import discord
from discord.ext import commands
from Utils.Logger import Logger

# === Role IDs ===
ADMIN_ROLE_IDS = [1290261005955235840, 1308763721316958261]  # Admin role IDs for Void-Bot

class SayCommand(commands.Cog):
    """
    🗣️ Say Command Cog: Allows admins to send messages as the bot.
    """

    def __init__(self, bot):
        self.bot = bot

    def create_say_embed(self, message, bot_user):
        embed = discord.Embed(description=message)  # Removed color=PINK
        # Removed set_pink_footer
        return embed

    # !say (Prefix) - Only prefix, no slash
    @commands.command(name="say")
    async def say(self, ctx, *, message: str):
        """
        🗣️ Allows an admin to send a message as the bot in the current channel.
        Usage: !say --embed your message here
        If --embed is included directly after !say, the message will be sent as an embed.
        """
        if not any(role.id in ADMIN_ROLE_IDS for role in ctx.author.roles):
            embed = discord.Embed(
                description="🚫 You do not have permission to use this command.",
                color=discord.Color.red()
            )
            # Removed set_pink_footer
            await ctx.send(embed=embed, delete_after=5)
            return
        await ctx.message.delete()
        if message.startswith("--embed "):
            message = message[8:].strip()
            embed = self.create_say_embed(message, self.bot.user)
            await ctx.send(embed=embed)
        else:
            await ctx.send(message)
        Logger.info(f"Prefix command !say used by {ctx.author} in {ctx.guild}")

async def setup(bot):
    """
    Setup function to add the SayCommand cog.
    """
    await bot.add_cog(SayCommand(bot))