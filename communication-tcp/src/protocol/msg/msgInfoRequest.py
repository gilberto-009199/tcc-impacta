from src.protocol.msg.msg import Msg

class MsgInfoRequest(Msg):

    def __init__(self, packet = []):
        self.packet = []

        if len(packet) == 0:
            pass

    def toPacket(self):
        return self.packet;

    @staticmethod
    def ofPacket(packet = []):
        return MsgInfoRequest(packet);
