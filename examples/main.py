from sealmc.fkrystal.pythonmc import PythonMC

from packets.login import LoginAcknowledgedPacket, LoginDisconnectPacket, LoginStartPacket, LoginSuccessPacket, MyLoginHandler, TransferPacket, MyTransferHandler
from packets.handshake import HandshakePacket, MyHandshakeHandler
from packets.status import StatusRequestPacket, StatusResponsePacket, PingPacket, MyStatusHandler

app = PythonMC(port=25565)

# Register Packets (State, ID, Class)
app.register_packet(0, 0x00, HandshakePacket)
app.register_packet(1, 0x00, StatusRequestPacket)
app.register_packet(1, 0x01, PingPacket)
app.register_packet(2, 0x00, LoginStartPacket)
app.register_packet(2, 0x02, LoginSuccessPacket)       # Server -> Client
app.register_packet(2, 0x03, LoginAcknowledgedPacket)  # Client -> Server (The Trigger)
app.register_packet(3, 0x0B, TransferPacket)
app.register_packet(3, 0x00, LoginStartPacket) # Register for Transfer too!

# Register Logic Handlers
app.set_handshake_state_handler(0, MyHandshakeHandler)
app.set_handshake_state_handler(1, MyStatusHandler)
app.set_handshake_state_handler(2, MyLoginHandler)
app.set_handshake_state_handler(3, MyTransferHandler) # Reuse Login logic for Transfer

if __name__ == "__main__":
    app.run()