import socket 
from .connection import Connection

class PythonMC:
    def __init__(self, host:str = "0.0.0.0", port: int=25565):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.handler_classes = {}
        self.registry = {}
        self.listeners = {}

    def register_packet(self, state_id, packet_id, packet_class):
        """User calls this to add packets."""
        if state_id not in self.registry:
            self.registry[state_id] = {}
        self.registry[state_id][packet_id] = packet_class
        packet_class.ID = packet_id 
        print(f"[API] Registered Packet: {packet_class.__name__} (State={state_id})")

    def set_handshake_state_handler(self, state_id: int, handler_class):
        """User calls this to add logic handlers."""
        self.handler_classes[state_id] = handler_class
        print(f"[API] Registered Logic: {handler_class.__name__} (State={state_id})")

    def get_packet_class(self, state_id, packet_id):
        return self.registry.get(state_id, {}).get(packet_id, None)

    def get_initial_handler(self, conn):
        if 0 not in self.handler_classes:
            raise RuntimeError("No Handshake Handler (State 0) defined!")
        return self.handler_classes[0](conn, self)

    def get_handler_for_state(self, state_id, conn):
        if state_id in self.handler_classes:
            return self.handler_classes[state_id](conn, self)
        return None
    
    def on_packet(self, state_id, packet_id):
        def decorator(func):
            k = (state_id, packet_id)
            if k not in self.listeners: self.listeners[k] = []
            self.listeners[k].append(func)
            return func
        return decorator

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        print(f"[*] Server listening on {self.host}:{self.port}")
        while True:
            client, addr = self.sock.accept()
            conn = Connection(client, self)
            try: conn.handle_client()
            except Exception as e: print(f"Error: {e}")
            finally: conn.close()