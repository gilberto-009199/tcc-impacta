import base64
import secrets
import struct

from app.peer.protocol.msg.msg import Msg

class MsgPiece(Msg):

    def __init__(self, packet = []):
        self.packet = []

        if len(packet) == 0:
            pass

        self.identifier_file = secrets.token_bytes(32);
        self.identifier_piece = secrets.token_bytes(32);
        self.identifier_index = secrets.token_bytes(4);
        self.buffer = secrets.token_bytes(1024);


        if len(packet) != 0:
            self.parsePacket(packet)
        

    def parsePacket(self, packet):
        
        packet = packet[3:]

        index = 0
        self.identifier_file = packet[index: index + 32]

        index += 32
        self.identifier_piece = packet[index: index + 32]

        index += 32
        self.identifier_index = packet[index: index + 4]

        index += 4
        self.buffer = packet[index:]


    def toPacket(self):

        payload =  self.identifier_file + self.identifier_piece + self.identifier_index + self.buffer
        

        if len(payload) > 65535:
            raise ValueError(f"Payload muito grande: {len(payload)}")
        
        header = struct.pack('!BH', Msg.MSG_TYPE_PIECE, len(payload))
        
        packet = header + bytes(payload)

        return packet;

    @staticmethod
    def ofPacket(packet = []):
        return MsgPiece(packet);


    def __str__(self):
        try:

            return (f"{self.__class__.__name__}("
                    f"identifier_file: {base64.b64encode(self.identifier_file).decode('utf-8')}, "
                    f"identifier_piece: {base64.b64encode(self.identifier_piece).decode('utf-8')}, "
                    f"identifier_index: {base64.b64encode(self.identifier_index).decode('utf-8')}, "
                    f"buffer: {base64.b64encode(self.buffer).decode('utf-8')}"
                    f")")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"