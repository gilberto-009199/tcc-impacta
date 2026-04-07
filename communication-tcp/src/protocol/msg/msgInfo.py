import base64
import json
import secrets
import struct

from src.protocol.msg.msg import Msg

class MsgInfo(Msg):

    def __init__(self, packet = []):
        self.packet = packet
        self.feature = [0, 1, 0]
        self.identifier = secrets.token_bytes(160)
        
        self.macketit = [1,0,1,0,1,0,1,0]
        self.paresDiretos = [{
            "feature": [1, 0, 0]
        }, {
            "feature": [1, 0, 1]
        }, {
          "feature": [1, 1, 1]
        }]

        if len(packet) > 0:
            pass

        # attribute
        # feature 
        #  0  - open bluetooh 
        #  0  - open internet wan
        #  0  - open router piece
        # identifier  160 bytes
        # arvore macketit
        # pares diretos


    def toPacket(self):

        payload = json.dumps({
            "feature": self.feature,
            "identifier": base64.b64encode(self.identifier).decode('utf-8'),
            "macketit": self.macketit,
            "paresDiretos": self.paresDiretos,
        }).encode('utf-8')

        payload = bytes(payload)
        
        if len(payload) > 65535:
            raise ValueError(f"Payload muito grande: {len(payload)}")
        
        header = struct.pack('!BH', Msg.MSG_TYPE_INFO, len(payload))

        packet = header + payload

        return packet

    @staticmethod
    def ofPacket(packet = []):
        return MsgInfo(packet)
    
    def __str__(self):
        try:
            
            return (f"{self.__class__.__name__}("
                    f"feature: {self.feature}, "
                    f"identifier: {base64.b64encode(self.identifier).decode('utf-8')}"
                    f"macketit: {self.macketit}, "
                    f"paresDiretos: {self.paresDiretos}"
                    f")")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"