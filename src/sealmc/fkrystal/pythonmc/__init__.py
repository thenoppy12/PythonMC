import socket 
from .connection import Connection

class PythonMC:
    def __init__(self, host: str = "0.0.0.0", port: int=25565):
        """
        Build a core framework instance.
        
        :param self: what?
        :param host: Host (0.0.0.0 or 127.0.0.1)
        :type host: str
        :param port: Port to expose (Default=25565)
        :type port: int
        """
        self.host: str = host
        self.port: int = port
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.handler_classes = {}
        self.registry = {}
        self.listeners = {}

    def register_packet(self, state_id, packet_id, packet_class):
        """
        Register a type of packet.

        :param state_id: Handshake Intent ID the packet used from the client | (0: Handshaking, 1: Status/Ping, 2: Login(Play), 3: Transfer)
        :type state_id: int
        :param packet_id: ID of the packet | (IntentID: 1 and PacketID: 0x01 => Ping Packet)
        :type packet_id: int
        :param packet_class: Class of that packet (must extend Packet class)
        :type packet_class: type[sealmc.fkrystal.pythonmc.packet.Packet]
        """
        if state_id not in self.registry:
            self.registry[state_id] = {}
        self.registry[state_id][packet_id] = packet_class
        packet_class.ID = packet_id 
        print(f"[CORE] Registered Packet: {packet_class.__name__} (State={state_id})")

    def set_handshake_state_handler(self, state_id: int, handler_class):
        """
        Add a handler for specific packet (ID).

        :param state_id: Handshake Intent ID the packet used from the client | (0: Handshaking, 1: Status/Ping, 2: Login(Play), 3: Transfer)
        :type state_id: int
        :param handle_class: Class of that handler of the packet (must extend PacketHandler class)
        :type handle_class: type[sealmc.fkrystal.pythonmc.handler.PacketHandler]
        """
        self.handler_classes[state_id] = handler_class
        print(f"[CORE] Registered Handler: {handler_class.__name__} (State={state_id})")

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

    def run(self):
        """
        Start the core...?
        """
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        print(f"[*] Server listening on {self.host}:{self.port}")
        while True:
            client, addr = self.sock.accept()
            conn = Connection(client, self)
            print(f"\n[+] Client connected")
            try: conn.handle_client()
            except Exception as e: print(f"[CORE] Error: {e}")
            finally: conn.close()