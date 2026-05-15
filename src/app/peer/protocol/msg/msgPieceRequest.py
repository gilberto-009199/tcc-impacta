import base64
from email import header
import secrets
import struct

from app.peer.protocol.msg.msg import Msg

class MsgPieceRequest(Msg):

    def __init__(self, 
                 packet = [],
                 identifier_file = secrets.token_bytes(32),
                 identifier_piece = secrets.token_bytes(32),
                 identifier_index = secrets.token_bytes(2),
                 buffer_length = secrets.token_bytes(3)):
        self.packet = []

        self.identifier_file = identifier_file
        self.identifier_piece = identifier_piece
        self.identifier_index = identifier_index
        self.buffer_length = buffer_length
        
        if len(packet) != 0:
            self.parsePacket(packet)



    def parsePacket(self, packet):
        
        packet = packet[3:]

        index = 0
        self.identifier_file = packet[index: index + 32]

        index += 32
        self.identifier_piece = packet[index: index + 32]

        index += 32
        self.identifier_index = packet[index: index + 2]

        index += 2
        self.buffer_length = packet[index:]

    def toPacket(self):

        payload =  self.identifier_file + self.identifier_piece + self.identifier_index + self.buffer_length
    

        if len(payload) > 65535:
            raise ValueError(f"Payload muito grande: {len(payload)}")
        
        header = struct.pack('!BH', Msg.MSG_TYPE_PIECE_REQUEST, len(payload))

        packet = header + bytes(payload)

        return packet

    @staticmethod
    def ofPacket(packet = []):
        return MsgPieceRequest(packet=packet);


    def __str__(self):
        try:
            return (f"{self.__class__.__name__}("
                    f"identifier_file: {base64.b64encode(self.identifier_file).decode('utf-8')}, "
                    f"identifier_piece: {base64.b64encode(self.identifier_piece).decode('utf-8')}, "
                    f"identifier_index: {base64.b64encode(self.identifier_index).decode('utf-8')}, "
                    f"buffer_length: {base64.b64encode(self.buffer_length).decode('utf-8')}"
                    f")")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"
        
    
        
    def __eq__(self, other):
        """Compara se dois objetos são iguais."""
        if not isinstance(other, self.__class__):
            return False
        
        return (self.identifier_file == other.identifier_file and 
                self.identifier_piece == other.identifier_piece and 
                self.identifier_index == other.identifier_index and
                self.buffer_length == other.buffer_length)