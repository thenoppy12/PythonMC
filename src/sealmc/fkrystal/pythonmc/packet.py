import io

class Packet:
    """Abstract Base Class. User packets must inherit from this."""
    ID = 0x00

    def __init__(self, packet_id=None, data_bytes=b''):
        self.id = packet_id if packet_id is not None else self.ID
        self.raw_data = data_bytes
        self.stream = io.BytesIO(data_bytes)

    def encode(self) -> bytes:
        return self.raw_data

    @classmethod
    def decode(cls, stream_or_packet):
        if isinstance(stream_or_packet, Packet):
            stream = stream_or_packet.stream
        else:
            stream = stream_or_packet
        return cls._decode_body(stream)

    @classmethod
    def _decode_body(cls, stream):
        raise NotImplementedError

    def __repr__(self):
        if self.__class__ != Packet:
            return f"<{self.__class__.__name__} ID=0x{self.id:02X}>"
        return f"<RawPacket ID=0x{self.id:02X} Size={len(self.raw_data)}>"