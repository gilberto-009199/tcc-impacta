from src.protocol.msg.msg import Msg


class MsgHandShake(Msg):
    
    MSG_HAND_SHAKE_BANNER = b"MENSSAGEIRO_IMPACTA"

    def __init__(self, packet = []):
        self.packet = []

        if len(packet) == 0:
            pass
        
        # banner equals
        # feature 
        #  0  - open bluetooh 
        #  0  - open internet wan
        #  0  - open router piece
        # identifier  160 bytes


    def toPacket(self):
        return self.packet;

    @staticmethod
    def ofPacket(packet = []):
        return MsgHandShake(packet);

