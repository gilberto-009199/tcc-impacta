from src.protocol.msg.msg import Msg

class MsgKeepAlive(Msg):

    def __init__(self, packet = [0]):
        self.packet = packet

    def toPacket(self):
        
        header  = bytes([Msg.MSG_TYPE_KEEP_ALIVE])
        payload =  bytes(self.packet)
        
        return header + payload

    @staticmethod
    def ofPacket(packet = []):
        return MsgKeepAlive(packet);
