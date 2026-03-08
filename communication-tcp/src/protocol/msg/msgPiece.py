from src.protocol.msg.msg import Msg

class MsgPiece(Msg):

    def __init__(self, packet = []):
        self.packet = []

        if len(packet) == 0:
            pass

        # attribute
        # IDENTIFIER DATA 
        # PIECE[Z:Y] FOR DATA IN IDENTIFIER
        # DATA FOR IDENTIFIER
        
    def toPacket(self):
        return self.packet;

    @staticmethod
    def ofPacket(packet = []):
        return MsgPiece(packet);
