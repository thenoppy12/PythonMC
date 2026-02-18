from .connection import Connection
from . import PythonMC

class PacketHandler:
    """A base handler for packets, specified by its ID"""
    def __init__(self, connection: Connection, server: PythonMC):
        self.conn: Connection = connection;self.server: PythonMC = server

    def handle(self, packet):
        method_name = f"handle_0x{packet.id:02x}"
        if hasattr(self, method_name): return getattr(self, method_name)(packet)
        else: print(f"[{self.__class__.__name__}] Ignored: 0x{packet.id:02x}");return self