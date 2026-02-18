import io

class Packet:
    """A base class for all packets."""
    ID = 0x00

    def __init__(self, packet_id=None, raw: bytes=b''):
        """
        Initialize a packet.

        :param packet_id: ID of packet. Normally you don't need to specify this.
        :type packet_id: (int, optional)
        :param raw: Default bytes of this packet. Normally you don't need to specify this.
        :type raw: (bytes, optional)
        
        """
        self.id = packet_id if packet_id is not None else self.ID
        self.raw: bytes = raw
        self.stream: io.BytesIO = io.BytesIO(raw)
    
    def send(self) -> bytes:
        """
        Produce your way to construct this packet into chunk of bytes

        Returns:
            bytes: Minecraft-styled bytes ready to send to the client.
        """
        return self.raw

    @classmethod
    def on_receive(cls, stream_or_packet):
        """
        The manager of the "receive_body" method\n
        This handle the entrie instance of packet.

        :param stream_or_packet: Your bytes stream... or the Packet class?
        :type stream_or_packet: io.BytesIO or Packet
        
        """
        if isinstance(stream_or_packet, Packet):
            stream = stream_or_packet.stream
        else:
            stream = stream_or_packet
        return cls.receive_body(stream)

    @classmethod
    def receive_body(cls, stream: io.BytesIO):
        """
        Act like a worker for "on_receive" method\n
        Produce your way to convert bytes into Python-styled objects

        :param stream: Your bytes stream.
        :type packet_id: io.BytesIO
        
        Raises:
            NotImplementedError: Ehm... You did not tell the worker how to convert it yet, lmfao.
        """
        raise NotImplementedError
    
    @classmethod
    def log(cls, level: str, message: str):
        """
        Simply log the packet with your provided message\n
        Ex: [PacketClass] [Level] your message.

        :param level: Level of your message (INFO, WARN, ERROR, FATAL, debug, etc...)
        :type level: str
        :param message: ur message..?
        :type message: str
        """
        print(f"[{cls.__name__}] [{level}] {message}")

    def __repr__(self):
        """
        If you want a way to debug your packet, try building your "reproduce" here\n
        Ex: 
        ```
            >>> packet
            "<CustomPacket Intent=3 Host=your.server Port=25565>"
        ```
        """
        if self.__class__ != Packet:
            return f"<{self.__class__.__name__} ID=0x{self.id:02X}>"
        return f"<RawPacket ID=0x{self.id:02X} Size={len(self.raw)}>"