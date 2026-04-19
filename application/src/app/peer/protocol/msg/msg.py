class Msg:

    # IDENTIFICADOR
    MSG_TYPE_HAND_SHAKE = 0b00000001 # 1
    MSG_TYPE_KEEP_ALIVE = 0b00000010 # 2

    MSG_TYPE_INFO = 0b00000011 # 3
    MSG_TYPE_INFO_REQUEST = 0b00000100 # 4

    MSG_TYPE_PIECE = 0b00000101 # 5
    MSG_TYPE_PIECE_REQUEST = 0b00000110 # 6
    
    def __init__(self, packet = []):
        self.packet = packet

    def toPacket(self):
        return self.packet

    @staticmethod
    def ofPacket(packet = []):
        return Msg(packet);

    def __str__(self):
        try:
            return (f"{self.__class__.__name__}("
                    f"packet: {self.packet.hex()}"
                    f")")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"