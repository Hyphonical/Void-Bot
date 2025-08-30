# 📦 Built-in modules
import base64
import io

# 📥 Custom modules
from Utils.Socket import GetStatus

# 👾 Discord modules
from discord.ext import commands
import discord


# 💡 Strip Minecraft color codes (e.g., §a, §l)
def StripColorCodes(Text: str) -> str:
	Out = []
	_ = 0
	while _ < len(Text):
		if Text[_] == '§' and _ + 1 < len(Text):
			_ += 2
			continue
		Out.append(Text[_])
		_ += 1
	return ''.join(Out)


# 💡 Format the "description" field from status JSON
def FormatDescription(Desc) -> str:
	if isinstance(Desc, str):
		return StripColorCodes(Desc)
	if isinstance(Desc, dict):
		Text = Desc.get('text', '')
		Extra = Desc.get('extra', [])
		Parts = [Text] + [FormatDescription(E) for E in Extra]
		return StripColorCodes(''.join(Parts)).strip() or 'No description'
	return 'No description'


class Minecraft(commands.Cog):
	def __init__(self, Bot: commands.Bot) -> None:
		self.Bot = Bot

	@commands.hybrid_command(name='mcstatus', description='Get Minecraft server status')
	async def MCStatus(self, ctx: commands.Context, host: str, port: int = 25565) -> None:
		try:
			# 🌐 Fetch server status
			Status = GetStatus(host, port)

			# 📊 Format the response as an embed
			Version = Status.get('version', {}).get('name', 'Unknown')
			PlayersOnline = Status.get('players', {}).get('online', 0)
			PlayersMax = Status.get('players', {}).get('max', 0)
			Description = FormatDescription(Status.get('description', 'No description'))
			FaviconUrl = Status.get('favicon')

			Embed = discord.Embed(
				title=f'Minecraft Server Status for {host}:{port}',
				color=0xA0D6B4,
			)
			Embed.add_field(name='Version', value=Version, inline=True)
			Embed.add_field(name='Players', value=f'{PlayersOnline}/{PlayersMax}', inline=True)
			Embed.add_field(name='Description', value=Description, inline=False)

			# 🖼️ Add server logo if available
			File = None
			if FaviconUrl and ',' in FaviconUrl:
				# Decode base64 and create file attachment
				Base64Data = FaviconUrl.split(',', 1)[1]
				ImageData = base64.b64decode(Base64Data)
				ImageBuffer = io.BytesIO(ImageData)
				ImageBuffer.seek(0)
				File = discord.File(ImageBuffer, 'favicon.png')
				Embed.set_thumbnail(url='attachment://favicon.png')
				await ctx.send(embed=Embed, file=File)
			else:
				await ctx.send(embed=Embed)
		except Exception as E:
			await ctx.send(f'❌ Failed to fetch server status: {str(E)}')


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Minecraft(Bot))
