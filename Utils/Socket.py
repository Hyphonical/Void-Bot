# 📦 Built-in modules
import socket
import struct
import json

# ⚙️ Settings
from Config import ProtocolVersion


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
