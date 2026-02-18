import json

from sealmc.fkrystal.pythonmc.packet import Packet
from sealmc.fkrystal.pythonmc.handler import PacketHandler
from sealmc.fkrystal.pythonmc.mctypes import MinecraftTypes
from sealmc.fkrystal.pythonmc.connection import Connection

class LoginStartPacket(Packet):
    def __init__(self, name=""):
        super().__init__()
        self.name = name
    @classmethod
    def receive_body(cls, stream):
        return cls(MinecraftTypes.read_string(stream))

class LoginDisconnectPacket(Packet):
    def __init__(self, text):
        super().__init__()
        self.text = text
    def send(self):
        data = {"text": self.text, "color": "red"}
        return MinecraftTypes.write_string(json.dumps(data))

class LoginSuccessPacket(Packet):
    # State: 2 (Login), ID: 0x02
    def __init__(self, uuid, username):
        super().__init__()
        self.uuid = uuid
        self.username = username
        
    def send(self):
        # UUID (16 bytes) + Username (String) + No Properties (VarInt 0)
        # For simplicity, we can use a zeroed UUID if you don't have one
        import uuid
        u = uuid.UUID(self.uuid).bytes
        return u + MinecraftTypes.write_string(self.username) + MinecraftTypes.write_varint(0)

class LoginAcknowledgedPacket(Packet):
    # State: 2 (Login), ID: 0x03 (Received from Client)
    # No body, just the ID.
    @classmethod
    def receive_body(cls, stream):
        return cls()


class MyLoginHandler(PacketHandler):
    def handle_0x00(self, p: LoginStartPacket):
        print(f"Login Start: {p.name}. Sending Success...")
        
        # A. Send Login Success (This triggers the client to send Ack)
        # Use a fake UUID for offline mode
        fake_uuid = "00000000-0000-0000-0000-000000000000" 
        self.conn.send_packet(LoginSuccessPacket(fake_uuid, p.name))
        
        # B. Stay in this handler, waiting for 0x03 (Ack)
        return self
    
    def handle_0x03(self, p: LoginAcknowledgedPacket):
        print(">> Switching to Config & Transferring...")
        
        # 1. Switch State Locally
        self.conn.switch_state(3)
        
        # 2. Send Transfer (Now valid because we are in State 3 context)
        # NOTE: Clients expect this packet immediately in Config state
        t_packet = TransferPacket("localhost", 25565)
        
        # We manually send it with ID 0x0B
        # Since we just switched self.conn.state to 3, send_packet might try to look up
        # the ID if we pass the object. Ensure TransferPacket is registered to State 3.
        self.conn.send_packet(t_packet)
        
        print(">> Transfer Packet Sent!")
        return self # Or return a ConfigHandler if you plan to do more
    
class MyTransferHandler(PacketHandler):
    def handle_0x00(self, p: LoginStartPacket):
        print(f"Transfer Start: {p.name}. Sending Success...")
        
        # A. Send Login Success (This triggers the client to send Ack)
        # Use a fake UUID for offline mode
        fake_uuid = "00000000-0000-0000-0000-000000000000" 
        self.conn.send_packet(LoginSuccessPacket(fake_uuid, p.name))
        
        # B. Stay in this handler, waiting for 0x03 (Ack)
        return self
    def handle_0x03(self, p: LoginAcknowledgedPacket):
        print(">> Switching to Config & Transferring...")
        
        # 1. Switch State Locally
        self.conn.switch_state(3)
        
        # 2. Send Transfer (Now valid because we are in State 3 context)
        # NOTE: Clients expect this packet immediately in Config state
        t_packet = TransferPacket("localhost", 25565)
        
        # We manually send it with ID 0x0B
        # Since we just switched self.conn.state to 3, send_packet might try to look up
        # the ID if we pass the object. Ensure TransferPacket is registered to State 3.
        self.conn.send_packet(t_packet)
        
        print(">> Transfer Packet Sent!")
        return self # Or return a ConfigHandler if you plan to do more


class TransferPacket(Packet):
    def __init__(self, host, port=25565):
        super().__init__()
        self.host = host
        self.port = port

    def send(self):
        return MinecraftTypes.write_string(self.host) + MinecraftTypes.write_varint(self.port)
