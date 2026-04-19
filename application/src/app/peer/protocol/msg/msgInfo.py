import base64
import json
import secrets
import struct

from app.peer.protocol.msg.msg import Msg

class MsgInfo(Msg):

    def __init__(self,
                packet = [],
                feature = [0, 1, 0],
                identifier = secrets.token_bytes(160),
                macketit = [1,0,1,0,1,0,1,0],
                peers = [
                    {"feature": [1, 0, 0]},
                    {"feature": [1, 0, 1]},
                    {"feature": [1, 1, 1]}
                ]
    ):
        self.packet = packet
        self.feature = feature
        self.identifier = identifier
        
        self.macketit = macketit
        self.peers = peers

        if len(packet) > 0:
            self.parsePacket(packet)
            pass

        # attribute
        # feature 
        #  0  - open bluetooh 
        #  0  - open internet wan
        #  0  - open router piece
        # identifier  160 bytes
        # arvore macketit
        # pares diretos


    def parsePacket(self, packet):
        packet = packet[3:]
        
        payload = json.loads(packet.decode('utf-8'))
        self.feature = payload.get("feature", [0, 0, 0])
        self.identifier = base64.b64decode(payload.get("identifier", ""))
        self.macketit = payload.get("macketit", [])
        self.peers = payload.get("peers", [])

    def toPacket(self):

        payload = json.dumps({
            "feature": self.feature,
            "identifier": base64.b64encode(self.identifier).decode('utf-8'),
            "macketit": self.macketit,
            "peers": self.peers,
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
                    f"peers: {self.peers}"
                    f")")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"