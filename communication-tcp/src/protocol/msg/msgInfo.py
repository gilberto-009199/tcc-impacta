from src.protocol.msg.msg import Msg

class MsgInfo(Msg):

    def __init__(self, packet = [0]):
        self.packet = []

        if len(packet) > 0:
            pass

        # attribute
        # feature 
        #  0  - open bluetooh 
        #  0  - open internet wan
        #  0  - open router piece
        # identifier  160 bytes
        # arvore macketit
        # pares diretos
        # pares indiretos 

    def toPacket(self):

        payload =  bytes(self.packet)
        header  = bytes(Msg.MSG_TYPE_INFO) + bytes([len(payload)])
        
        
        return header + payload;

    @staticmethod
    def ofPacket(packet = []):
        return MsgInfo(packet);
