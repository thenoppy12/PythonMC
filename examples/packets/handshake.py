from sealmc.fkrystal.pythonmc.packet import Packet
from sealmc.fkrystal.pythonmc.handler import PacketHandler
from sealmc.fkrystal.pythonmc.mctypes import MinecraftTypes


class HandshakePacket(Packet):
    def __init__(self, ver=0, addr="", port=25565, state=0):
        super().__init__()
        self.ver = ver
        self.addr = addr
        self.port = port
        self.state = state
    @classmethod
    def receive_body(cls, stream):
        return cls(MinecraftTypes.read_varint(stream), MinecraftTypes.read_string(stream), MinecraftTypes.read_ushort(stream), MinecraftTypes.read_varint(stream))
    def __repr__(self): return f"<Handshake Protocol={self.ver} Intent={self.state}>"
    
class MyHandshakeHandler(PacketHandler):
    def handle_0x00(self, p: HandshakePacket):
        print(f"Handshake from {p.addr} -> Requesting State {p.state}")
        print(f"[DEBUG]", p)
        self.conn.switch_state(p.state)
        return self.server.get_handler_for_state(p.state, self.conn)