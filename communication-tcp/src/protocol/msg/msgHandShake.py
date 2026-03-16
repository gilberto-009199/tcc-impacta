import secrets
from src.protocol.msg.msg import Msg


class MsgHandShake(Msg):
    
    MSG_HAND_SHAKE_BANNER = b"MENSSAGEIRO_IMPACTA"

    def __init__(self, packet = []):
        # banner 
        # feature 
        #  0  - open bluetooh 
        #  0  - open internet wan
        #  0  - open router piece
        # identifier  160 bytes

        self.packet = []
        self.banner = self.MSG_HAND_SHAKE_BANNER
        self.feature = [0, 0, 0]
        self.identifier = secrets.token_bytes(160)

        
        if len(packet) != 0:
            self.parsePacket(packet)
        

    def parsePacket(self, packet):
        index = 0
        self.banner = packet[index:self.MSG_HAND_SHAKE_BANNER.__len__()]
        index += self.MSG_HAND_SHAKE_BANNER.__len__()
        self.feature = list(packet[index:index + 3])
        index += 3
        self.identifier = packet[index:index + 160]

    def toPacket(self):
        return self.banner + bytes(self.feature) + self.identifier

    @staticmethod
    def ofPeer(peer):
        msg = MsgHandShake()
        msg.banner = msg.MSG_HAND_SHAKE_BANNER
        msg.feature = peer.feature if peer.feature is not None else [0, 0, 0]
        msg.identifier = peer.identifier if peer.identifier is not None else secrets.token_bytes(160)
        return msg

    @staticmethod
    def ofPacket(packet = []):
        return MsgHandShake(packet);

