from src.protocol.msg.msg import Msg

class MsgInfoRequest(Msg):

    def __init__(self, packet = []):
        self.packet = []

        if len(packet) == 0:
            pass

    def toPacket(self):
        
        payload =  bytes(self.packet)
        header  = bytes(Msg.MSG_TYPE_INFO_REQUEST) + bytes([len(payload)])

        return header + payload;

    @staticmethod
    def ofPacket(packet = []):
        return MsgInfoRequest(packet);
