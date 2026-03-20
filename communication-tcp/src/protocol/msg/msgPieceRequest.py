from src.protocol.msg.msg import Msg

class MsgPieceRequest(Msg):

    def __init__(self, packet = []):
        self.packet = []

        if len(packet) == 0:
            pass

        # atribute
        # IDENTIFIER DATA 
        # PIECE[Z:Y] FOR DATA IN IDENTIFIER
        

    def toPacket(self):
        header  = bytes([Msg.MSG_TYPE_PIECE_REQUEST])
        payload =  bytes(self.packet)
        
        return header + payload;

    @staticmethod
    def ofPacket(packet = []):
        return MsgPieceRequest(packet);
