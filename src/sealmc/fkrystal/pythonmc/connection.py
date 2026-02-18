import io, struct, socket

from .mctypes import MinecraftTypes
from .packet import Packet

class Connection:
    def __init__(self, sock: socket.socket, server):
        self.sock = sock
        self.server = server
        self.stream = sock.makefile('rb')
        self.state = 0 
        
    def read_next_packet(self):
        try:
            try:
                length = MinecraftTypes.read_varint(self.stream)
            except (EOFError, ConnectionResetError):
                return None
            body = self.stream.read(length)
            if len(body) < length: return None
            body_stream: io.BytesIO = io.BytesIO(body)
            p_id = MinecraftTypes.read_varint(body_stream)
            packet_class: Packet = self.server.get_packet_class(self.state, p_id)
            if packet_class:
                return packet_class.on_receive(body_stream)
            else:
                return Packet(p_id, body_stream.read())
        except (Exception, struct.error) as e:
            print(f"[CONN] Read Error: {e}")
            return None
        
    def send_packet(self, packet_or_id, payload=b''):
        if isinstance(packet_or_id, Packet):
            p_id = packet_or_id.ID
            data = packet_or_id.send()
        else:
            p_id = packet_or_id
            data = payload
        id_bytes = MinecraftTypes.write_varint(p_id)
        total_len = MinecraftTypes.write_varint(len(id_bytes) + len(data))
        self.sock.sendall(total_len + id_bytes + data)

    def close(self):
        self.sock.close()

    def switch_state(self, new_state):
        self.state = new_state

    def handle_client(self):
        current_handler = self.server.get_initial_handler(self)
        while True:
            packet = self.read_next_packet()
            if not packet: break
            next_handler = current_handler.handle(packet)
            if next_handler is not current_handler:
                current_handler = next_handler