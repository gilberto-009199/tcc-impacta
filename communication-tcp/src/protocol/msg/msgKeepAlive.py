from src.protocol.msg.msg import Msg

class MsgKeepAlive(Msg):

    def __init__(self, packet = [0]):
        self.packet = packet

    def toPacket(self):
        
        payload =  bytes(self.packet)
        header  = bytes(Msg.MSG_TYPE_KEEP_ALIVE) + bytes([len(payload)])

        return header + payload

    @staticmethod
    def ofPacket(packet = []):
        return MsgKeepAlive(packet);
