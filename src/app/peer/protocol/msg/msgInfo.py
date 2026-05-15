import base64
import json
import secrets
import struct

from app.peer.protocol.msg.msg import Msg

class MsgInfo(Msg):

    def __init__(self,
                packet = [],
                feature = [0, 1, 0],
                identifier = base64.b64encode(secrets.token_bytes(160)).decode('utf-8'),
                files = [],
                peers = []
    ):
        self.packet = packet
        self.feature = feature
        self.identifier = identifier
        
        self.files = files
        self.peers = peers

        if len(packet) > 0:
            self.parsePacket(packet)
            pass



    def parsePacket(self, packet):
        packet = packet[3:]
        
        payload = json.loads(packet.decode('utf-8'))
        self.feature = payload.get("feature", [0, 0, 0])
        self.identifier = payload.get("identifier", "")
        self.files = payload.get("files", [])
        self.peers = payload.get("peers", [])

    def toPacket(self):

        payload = json.dumps({
            "feature": self.feature,
            "identifier": self.identifier,
            "files": self.files,
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
        return MsgInfo(packet=packet)
    
    def __str__(self):
        try:
            
            return (f"{self.__class__.__name__}("
                    f"feature: {self.feature}, "
                    f"identifier: {self.identifier}"
                    f"files: {self.files}, "
                    f"peers: {self.peers}"
                    f")")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"
    
    def __eq__(self, other):
        """Compara se dois objetos são iguais."""
        if not isinstance(other, self.__class__):
            return False
        
        return (self.feature == other.feature and 
                self.identifier == other.identifier and 
                self.files == other.files and 
                self.peers == other.peers)
