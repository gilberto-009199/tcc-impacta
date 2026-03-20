from src.protocol.msg.msg import Msg

class MsgInfoRequest(Msg):

    def __init__(self, packet = []):
        self.packet = []

        if len(packet) == 0:
            pass

    def toPacket(self):
        header  = bytes([Msg.MSG_TYPE_INFO_REQUEST])
        payload =  bytes(self.packet)
        return header + payload;

    @staticmethod
    def ofPacket(packet = []):
        return MsgInfoRequest(packet);
