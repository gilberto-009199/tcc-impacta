from src.protocol.msg.msg import Msg

class MsgKeepAlive(Msg):

    def __init__(self, packet = [1]):
        self.packet = packet

    def toPacket(self):
        return Msg.MSG_TYPE_KEEP_ALIVE + bytes(self.packet);

    @staticmethod
    def ofPacket(packet = []):
        return MsgKeepAlive(packet);
