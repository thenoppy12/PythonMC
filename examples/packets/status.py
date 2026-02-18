import json

from sealmc.fkrystal.pythonmc.packet import Packet
from sealmc.fkrystal.pythonmc.handler import PacketHandler
from sealmc.fkrystal.pythonmc.mctypes import MinecraftTypes


class StatusRequestPacket(Packet):
    # ID 0x00 in State 1
    def __init__(self): super().__init__()
    @classmethod
    def receive_body(cls, stream): return cls()

class PingPacket(Packet):
    # ID 0x01 in State 1
    def __init__(self, payload=0):
        super().__init__()
        self.payload = payload
    @classmethod
    def receive_body(cls, stream): return cls(MinecraftTypes.read_long(stream))
    def send(self): return MinecraftTypes.write_long(self.payload)

class StatusResponsePacket(Packet):
    # We only send this, never receive it
    def __init__(self, json_dict):
        super().__init__()
        self.data = json.dumps(json_dict)
    def send(self): return MinecraftTypes.write_string(self.data)


class MyStatusHandler(PacketHandler):
    def handle_0x00(self, p: StatusRequestPacket):
        # 1. Received Request -> Send JSON Response
        with open("config/status.json", "r") as fstat:
            status = json.load(fstat)
        self.conn.send_packet(StatusResponsePacket(status))
        return self

    def handle_0x01(self, p: PingPacket):
        # 2. Received Ping -> Send Pong
        print(f"Ping: {p.payload}")
        self.conn.send_packet(PingPacket(p.payload))
        return self
