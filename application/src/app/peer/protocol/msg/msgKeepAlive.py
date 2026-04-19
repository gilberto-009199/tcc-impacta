from email import header
import struct

from app.peer.protocol.msg.msg import Msg

class MsgKeepAlive(Msg):

    def __init__(self, packet = []):
        pass

    def toPacket(self):
        
        
        header = struct.pack('!BH', Msg.MSG_TYPE_KEEP_ALIVE, 0)

        packet = header

        return packet

    @staticmethod
    def ofPacket(packet = []):
        return MsgKeepAlive(packet);


    def __str__(self):
        try:
            
            return (f"{self.__class__.__name__}()")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"