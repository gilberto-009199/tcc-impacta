import base64
import json
import secrets
import struct

from app.peer.protocol.msg.msg import Msg


class MsgHandShake(Msg):
    
    MSG_HAND_SHAKE_BANNER = b"MENSSAGEIRO_IMPACTA"
    MSG_HAND_SHAKE_LENGTH = 1 + len(MSG_HAND_SHAKE_BANNER) + 3 + 160

    def __init__(self, packet = []):
        self.packet = []
        self.banner = self.MSG_HAND_SHAKE_BANNER
        self.feature = [0, 0, 0]
        self.identifier = base64.b64encode(secrets.token_bytes(160)).decode('utf-8')

        
        if len(packet) != 0:
            self.parsePacket(packet)
        

    def parsePacket(self, packet):
        
        packet = packet[3:]

        self.banner = packet[:self.MSG_HAND_SHAKE_BANNER.__len__()]
        
        jsonpacket = json.loads(packet[self.MSG_HAND_SHAKE_BANNER.__len__():].decode('utf-8'))

        self.feature = list(jsonpacket["feature"])
        self.identifier = str(jsonpacket["identifier"])

    def toPacket(self):
        
        payload = json.dumps({
            "feature": self.feature,
            "identifier": self.identifier
        }).encode('utf-8')

        payload = self.banner + bytes(payload)
        

        if len(payload) > 65535:
            raise ValueError(f"Payload muito grande: {len(payload)}")
        
        header = struct.pack('!BH', Msg.MSG_TYPE_HAND_SHAKE, len(payload))
    
        packet = header + payload

        return packet

    @staticmethod
    def ofPeer(identifier, feature):
        msg = MsgHandShake()
        msg.banner = msg.MSG_HAND_SHAKE_BANNER
        msg.feature = feature if feature is not None else [0, 0, 0]
        msg.identifier = identifier if identifier is not None else base64.b64encode(secrets.token_bytes(160)).decode('utf-8')
        return msg

    @staticmethod
    def ofPacket(packet = []):
        return MsgHandShake(packet=packet);

    def __str__(self):
        try:
            
            return (f"{self.__class__.__name__}("
                    f"banner: {self.banner}, "
                    f"feature: {self.feature}, "
                    f"identifier: {self.identifier}"
                    f")")
        except Exception as e:
            return f"{self.__class__.__name__}(parse_error: {e})"
        
    def __eq__(self, other):
        """Compara se dois objetos são iguais."""
        if not isinstance(other, self.__class__):
            return False
        
        return (self.banner == other.banner and 
                self.feature == other.feature and 
                self.identifier == other.identifier)
    