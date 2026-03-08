from src.protocol.msg.msg import Msg

class Msg:

    # IDENTIFICADOR
    MSG_TYPE_HANDSHAKE = 0x01
    MSG_TYPE_KEEP_ALIVE = 0x02
    
    MSG_TYPE_INFO = 0x03
    MSG_TYPE_INFO_REQUEST = 0x04
    
    MSG_TYPE_PIECE = 0x05
    MSG_TYPE_PIECE_REQUEST = 0x06
    
    
    def __init__(self, packet = []):
        self.packet = []

    def toPacket(self):
        return self.packet;

    @staticmethod
    def ofPacket(packet = []):
        return Msg(packet);
