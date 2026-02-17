# No imports of specific packets here!
class PacketHandler:
    """Base Logic Handler. Users inherit this to define game states."""
    def __init__(self, connection, server):
        self.conn = connection
        self.server = server

    def handle(self, packet):
        method_name = f"handle_0x{packet.id:02x}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(packet)
        else:
            print(f"[{self.__class__.__name__}] Ignored: 0x{packet.id:02x}")
            return self