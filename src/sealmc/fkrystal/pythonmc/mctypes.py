import struct

class MinecraftTypes:
    """Static methods for encoding/decoding Minecraft primitives."""
    
    @staticmethod
    def read_varint(stream):
        val = 0
        shift = 0
        while True:
            byte = stream.read(1)
            if len(byte) == 0: raise EOFError("Socket closed during VarInt")
            b = byte[0]
            val |= (b & 0x7F) << shift
            if not (b & 0x80):
                return val
            shift += 7

    @staticmethod
    def write_varint(val):
        """Encodes an integer as a VarInt bytes object."""
        total = b''
        while True:
            tobytes = val & 0x7F
            val >>= 7
            if val:
                total += bytes([tobytes | 0x80])
            else:
                total += bytes([tobytes])
                return total

    @staticmethod
    def read_string(stream):
        """Reads a VarInt length, then that many bytes as UTF-8."""
        length = MinecraftTypes.read_varint(stream)
        data = stream.read(length)
        if len(data) < length: raise EOFError("String incomplete")
        return data.decode('utf-8')

    @staticmethod
    def write_string(text):
        """Encodes a string with VarInt length prefix."""
        data = text.encode('utf-8')
        return MinecraftTypes.write_varint(len(data)) + data

    @staticmethod
    def read_ushort(stream):
        """Reads an Unsigned Short (2 bytes, Big Endian). e.g. Port."""
        return struct.unpack('>H', stream.read(2))[0]

    @staticmethod
    def read_long(stream):
        # 1. Read 8 bytes
        data = stream.read(8)
        if len(data) < 8:
            raise struct.error(f"read_long expected 8 bytes, got {len(data)}. Stream pos: {stream.tell()}")
        # 3. Unpack
        return struct.unpack('>q', data)[0]
    
    @staticmethod
    def write_long(val):
        """Writes a Long (8 bytes, Big Endian)."""
        return struct.pack('>q', val)