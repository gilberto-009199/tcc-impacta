import struct

from app.peer.protocol.msg.msg import Msg

class MsgInfoRequest(Msg):

    def __init__(self, packet = []):
        self.packet = packet

        if len(packet) == 0:
            pass

    def toPacket(self):
        
        payload =  bytes(self.packet)
        

        if len(payload) > 65535:
            raise ValueError(f"Payload muito grande: {len(payload)}")
        
        header = struct.pack('!BH', Msg.MSG_TYPE_INFO_REQUEST, len(payload))

        packet = header + bytes(payload)

        return packet

    @staticmethod
    def ofPacket(packet = []):
        return MsgInfoRequest(packet);


    def __str__(self):
        try:
            
            return (f"{self.__class__.__name__}()")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"