# <center>PythonMC

### This is a simple framework (not API) to reproduce Minecraft: Java Edition protocol

### Usage:
```py
import json
# src.sealmc... if you clone this repo
from src.sealmc.fkrystal.pythonmc import PythonMC
from src.sealmc.fkrystal.pythonmc.packet import Packet
from src.sealmc.fkrystal.pythonmc.handler import PacketHandler
from src.sealmc.fkrystal.pythonmc.mctypes import MinecraftTypes

# or if you install with pip or uv...
from sealmc.fkrystal.pythonmc import PythonMC
from sealmc.fkrystal.pythonmc.packet import Packet
from sealmc.fkrystal.pythonmc.handler import PacketHandler
from sealmc.fkrystal.pythonmc.mctypes import MinecraftTypes



# ==========================================
# Add your packet structure
# ==========================================

# https://minecraft.wiki/w/Java_Edition_protocol/Packets#Handshaking
class HandshakePacket(Packet):
    def __init__(self, ver=0, addr="", port=25565, state=1):
        super().__init__()
        self.ver = ver
        self.addr = addr
        self.state = state
    @classmethod
    def _decode_body(cls, stream):
        return cls(MinecraftTypes.read_varint(stream), MinecraftTypes.read_string(stream), MinecraftTypes.read_ushort(stream), MinecraftTypes.read_varint(stream))
    def __repr__(self): return f"<Handshake Protocol={self.ver} Intent={self.state}>"

# https://minecraft.wiki/w/Java_Edition_protocol/Packets#Login
class LoginStartPacket(Packet):
    def __init__(self, name=""):
        super().__init__()
        self.name = name
    @classmethod
    def _decode_body(cls, stream):
        return cls(MinecraftTypes.read_string(stream))

class LoginDisconnectPacket(Packet):
    def __init__(self, text):
        super().__init__()
        self.text = text
    def encode(self):
        data = {"text": self.text, "color": "red"}
        return MinecraftTypes.write_string(json.dumps(data))

# https://minecraft.wiki/w/Java_Edition_protocol/Packets#Status
class StatusRequestPacket(Packet):
    # ID 0x00 in State 1
    def __init__(self): super().__init__()
    @classmethod
    def _decode_body(cls, stream): return cls()

class PingPacket(Packet):
    # ID 0x01 in State 1
    def __init__(self, payload=0):
        super().__init__()
        self.payload = payload
    @classmethod
    def _decode_body(cls, stream): return cls(MinecraftTypes.read_long(stream))
    def encode(self): return MinecraftTypes.write_long(self.payload)

class StatusResponsePacket(Packet):
    # We only send this, never receive it
    def __init__(self, json_dict):
        super().__init__()
        self.data = json.dumps(json_dict)
    def encode(self): return MinecraftTypes.write_string(self.data)

# ==========================================
# Packet Handler
# ==========================================

class MyHandshakeHandler(PacketHandler):
    def handle_0x00(self, p: HandshakePacket):
        print(f"Handshake from {p.addr} -> Requesting State {p.state}")
        print(f"[DEBUG]", p)
        self.conn.switch_state(p.state)
        return self.server.get_handler_for_state(p.state, self.conn)

class MyLoginHandler(PacketHandler):
    def handle_0x00(self, p: LoginStartPacket):
        print(f"Login Attempt: {p.name}")
        # Kick them using our custom packet
        self.conn.send_packet(LoginDisconnectPacket(f"Welcome {p.name} (Login test)"))
        return self
    
class MyTransferHandler(PacketHandler):
    def handle_0x00(self, p: LoginStartPacket):
        print(f"Transfer Attempt: {p.name}")
        # Kick them using our custom packet
        self.conn.send_packet(LoginDisconnectPacket(f"Welcome {p.name} (Transfer test)"))
        return self

class MyStatusHandler(PacketHandler):
    def handle_0x00(self, p: StatusRequestPacket):
        # 1. Received Request -> Send JSON Response
        status = {
            "version": {"name": "PythonMC", "protocol": 47},
            "players": {"max": 100, "online": 1},
            "description": {"text": "Powered by Python!"}
        }
        self.conn.send_packet(StatusResponsePacket(status))
        return self

    def handle_0x01(self, p: PingPacket):
        # 2. Received Ping -> Send Pong
        print(f"Ping: {p.payload}")
        self.conn.send_packet(PingPacket(p.payload))
        return self
    


app = PythonMC(port=25565)

# Register Packets (State, ID, Class)
app.register_packet(0, 0x00, HandshakePacket)
app.register_packet(1, 0x00, StatusRequestPacket)
app.register_packet(1, 0x01, PingPacket)
app.register_packet(2, 0x00, LoginStartPacket)
app.register_packet(3, 0x00, LoginStartPacket) 

# Register Logic Handlers
app.set_handshake_state_handler(0, MyHandshakeHandler)
app.set_handshake_state_handler(1, MyStatusHandler)
app.set_handshake_state_handler(2, MyLoginHandler)
app.set_handshake_state_handler(3, MyTransferHandler) 

if __name__ == "__main__":
    app.run()
```