import struct

from app.peer.protocol.msg.msg import Msg

class MsgInfoRequest(Msg):

    def __init__(self, packet = []):
        self.packet = packet

        if len(packet) == 0:
            pass

    def toPacket(self):
        
        payload =  bytes(self.packet)
        
        if len(payload) > 4294967295:  # Máximo para 4 bytes (unsigned int)
            raise ValueError(f"Payload muito grande: {len(payload)}")
        
        header = struct.pack(
            '!BI',  # Mudado de '!BH' para '!BI' (4 bytes para o tamanho)
            Msg.MSG_TYPE_INFO_REQUEST,
            len(payload)
        )

        packet = header + bytes(payload)

        return packet

    @staticmethod
    def ofPacket(packet = []):
        return MsgInfoRequest(packet=packet);


    def __str__(self):
        try:
            
            return (f"{self.__class__.__name__}()")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"
    
        
    def __eq__(self, other):
        """Compara se dois objetos são iguais."""
        if not isinstance(other, self.__class__):
            return False
        
        return True
    