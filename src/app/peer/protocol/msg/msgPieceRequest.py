import base64
import secrets
import struct

from app.peer.protocol.msg.msg import Msg

import logging

logger = logging.getLogger(__name__)

class MsgPieceRequest(Msg):

    def __init__(self, 
                 packet = [],
                 identifier_file = secrets.token_bytes(20).hex(),
                 identifier_piece = 0,
                 identifier_index = 0,
                 buffer_length = 0):
        self.packet = []

        self.identifier_file = identifier_file
        self.identifier_piece = identifier_piece
        self.identifier_index = identifier_index
        self.buffer_length = buffer_length
        
        if len(packet) != 0:
            self.parsePacket(packet)


    def parsePacket(self, packet):
        try:
            packet = packet[5:]

            index = 0
            self.identifier_file = packet[index:index + 40].decode('utf-8')
            
            index += 40
            self.identifier_piece = struct.unpack('!H', packet[index: index + 2 ])[0]
            
            index += 2
            self.identifier_index = struct.unpack('!H', packet[index: index + 2 ])[0]

            index += 2
            self.buffer_length = struct.unpack('!I', packet[index:])[0]
        except Exception as e:
            tb = e.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            logger.info(f"Erro ao criar pacote parsePacket : {arquivo}:{linha}, linha: {linha}, e: {e}")

    def toPacket(self):
        try:
            # Convert fields to bytes
            identifier_file = self.identifier_file.encode('utf-8') if isinstance(self.identifier_file, str) else self.identifier_file
            
            if len(identifier_file) != 40:
                raise ValueError(f"identifier_file deve ter exatamente 40 bytes, mas tem {len(identifier_file)} bytes")
            
            # Pack integer fields
            identifier_piece = struct.pack('!H', self.identifier_piece)
            identifier_index = struct.pack('!H', self.identifier_index)
            buffer_length = struct.pack('!I', self.buffer_length)
            
            # Build payload
            payload = identifier_file + identifier_piece + identifier_index + buffer_length

            if len(payload) > 4294967295:  # Máximo para 4 bytes (unsigned int)
                    raise ValueError(f"Payload muito grande: {len(payload)}")
            
            header = struct.pack(
                '!BI',  # Mudado de '!BH' para '!BI' (4 bytes para o tamanho)
                Msg.MSG_TYPE_PIECE_REQUEST,
                len(payload)
            )

            packet = header + bytes(payload)

            return packet
        except Exception as e:
            tb = e.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            logger.info(f"Erro ao criar pacote toPacket : {arquivo}:{linha}, linha: {linha}")

    @staticmethod
    def ofPacket(packet = []):
        return MsgPieceRequest(packet=packet);


    def __str__(self):
        try:
            return (f"{self.__class__.__name__}("
                    f"identifier_file: {self.identifier_file}, "
                    f"identifier_piece: {self.identifier_piece}, "
                    f"identifier_index: {self.identifier_index}, "
                    f"buffer_length: {self.buffer_length}"
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
    

