import time
from src.protocol.msg.msgHandShake import MsgHandShake
import socket


class Peer:
    
    def __init__(self, socket, host, port, peerManager):
        self.socket = socket
        self.host = host
        self.port = port
        self.peerManager = peerManager

        self.identifier = None
        self.feature = None
        self.info = None

        self.hasSendHandshake = False
        self.hasRecvHandshake = False

        self.queueMsgRecv = []
        self.queueMsgSend = []

    def setSocket(self, socket):
        self.socket = socket;
    
    def sendMsg(self, msg):
        self.queueMsgSend.append(msg);

    def recvMsg(self, msg):
        self.queueMsgRecv.append(msg);



    def run(self):
        # lifecycle of peer connection
        if self.socket is None:
            return False
        
        # verify hasHandshake
        # if not hasHandshake then send MsgHandshake 
        if not self.hasSendHandshake or not self.hasRecvHandshake:
            self.handShake();

        # count  keep alive time 
        # if max time then send keep alive

        # send msg in queueMsgSend
        # recv msg in queueMsgRecv

        pass

    def handShake(self):
        try:
            
            if not self.hasRecvHandshake:
                
                print(f"Recebendo handshake de {self.host}:{self.port}...")
                data = self.socket.recv(1)
                print(f"handshake de {self.host}:{self.port}: " + data.decode())

                if len(data) == 1:
                    recv_handshake = MsgHandShake.ofPacket(data)
                    # if recv MsgHandshake is valid then hasHandshake = True
                    if recv_handshake.banner == MsgHandShake.MSG_HAND_SHAKE_BANNER:
                        self.identifier = recv_handshake.identifier
                        self.feature = recv_handshake.feature
                        self.hasRecvHandshake = True

            # send MsgHandshake
            if not self.hasSendHandshake:
                print(f"Enviando handshake para {self.host}:{self.port}...")
                handshake_msg = MsgHandShake.ofPeer(self.peerManager.peer)
                self.socket.send(handshake_msg.toPacket())
                self.hasSendHandshake = True

            

        except Exception as e:
            print(f"\t [PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            print(f"Handshake failed: {e}")
            self.disconnect()

    
    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.socket = None

