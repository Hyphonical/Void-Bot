# 📦 Built-in modules
import struct
import socket
import json

# ⚙️ Settings
from Config import ProtocolVersion

# 👾 Discord modules
from discord.ext import commands
import discord


# 💡 Helper function to pack a varint
def PackVarint(Value: int) -> bytes:
	Out = b''
	while True:
		Byte = Value & 0x7F
		Value >>= 7
		if Value:
			Out += struct.pack('B', Byte | 0x80)
		else:
			Out += struct.pack('B', Byte)
			break
	return Out


# 💡 Helper function to read exactly N bytes
def RecvExact(Sock: socket.socket, Count: int) -> bytes:
	Buf = b''
	while len(Buf) < Count:
		Chunk = Sock.recv(Count - len(Buf))
		if not Chunk:
			raise ConnectionError('Socket closed before receiving expected data')
		Buf += Chunk
	return Buf


# 💡 Helper function to read a varint from socket
def ReadVarint(Sock: socket.socket) -> int:
	Value = 0
	NumRead = 0
	while True:
		Byte = Sock.recv(1)
		if not Byte:
			raise ConnectionError('Socket closed while reading VarInt')
		ByteVal = Byte[0]
		Value |= (ByteVal & 0x7F) << (7 * NumRead)
		NumRead += 1
		if NumRead > 5:
			raise ValueError('VarInt too big')
		if (ByteVal & 0x80) != 0x80:
			break
	return Value


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


# 🌱 Function to get Minecraft server status
def GetStatus(Host: str, Port: int = 25565) -> dict:
	# 🔌 Connect to server
	Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	Sock.settimeout(5)
	try:
		Sock.connect((Host, Port))

		# 📤 Handshake packet
		HostBytes = Host.encode('utf-8')
		Data = (
			PackVarint(0)  # packet id
			+ PackVarint(ProtocolVersion)  # protocol version
			+ PackVarint(len(HostBytes))
			+ HostBytes
			+ struct.pack('>H', Port)  # port
			+ PackVarint(1)  # next state (status)
		)
		Sock.sendall(PackVarint(len(Data)) + Data)

		# 📤 Request packet
		Sock.sendall(PackVarint(1) + b'\x00')

		# 📥 Read response packet: [Length VarInt][PacketId VarInt][JsonLen VarInt][Json bytes]
		_ = ReadVarint(Sock)  # total packet length (ignored)
		PacketId = ReadVarint(Sock)  # should be 0 for status response
		if PacketId != 0:
			raise ValueError(f'Unexpected packet id: {PacketId}')
		StringLength = ReadVarint(Sock)
		Response = RecvExact(Sock, StringLength).decode('utf-8', errors='replace')

		return json.loads(Response)
	finally:
		try:
			Sock.close()
		except Exception:
			pass


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

			Embed = discord.Embed(
				title=f'Minecraft Server Status for {host}:{port}',
				color=0x00FF00,  # Green color for success
			)
			Embed.add_field(name='Version', value=Version, inline=True)
			Embed.add_field(name='Players', value=f'{PlayersOnline}/{PlayersMax}', inline=True)
			Embed.add_field(name='Description', value=Description, inline=False)

			await ctx.send(embed=Embed)
		except Exception as E:
			await ctx.send(f'❌ Failed to fetch server status: {str(E)}')


async def setup(Bot: commands.Bot) -> None:
	await Bot.add_cog(Minecraft(Bot))
