import time
from src.protocol.msg.msgKeepAlive import MsgKeepAlive
from src.protocol.msg.msgHandShake import MsgHandShake


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

        self.timeKeepAlive = 0;

        self.queueMsgRecv = []
        self.queueMsgSend = []

    def setSocket(self, socket):
        self.socket = socket;
    
    def sendMsg(self, msg):
        self.queueMsgSend.append(msg);

    def recvMsg(self, msg):
        self.queueMsgRecv.append(msg);

    # lifecycle of peer connection
    def run(self):

        if self.socket is None:
            return False

        # Handshake
        if not self.hasSendHandshake or not self.hasRecvHandshake:
            self.handShake();
            return True;

        # KeepAlive
        current_time = time.time()
        if current_time - self.timeKeepAlive >= 8:
            print(f"[PEER] Enviando keep alive para {self.host}:{self.port}")
            self.timeKeepAlive = current_time
            self.keepAlive()
            return True

        self.sendMsg();
    
        self.recvMsg();
        
        return True

    def sendMsg(self):
        pass
        """while len(self.queueMsgSend) > 0:
            msg = self.queueMsgSend.pop(0)
            try:
                if self.verifyconnection():
                    return

                self.socket.send(msg.toPacket())

            except Exception as e:
                print(f" [PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
                print(f"Handshake failed: {e}")
                self.disconnect()"""

    def recvMsg(self):
        try:
            if not self.validConnection():
                return

            data = self.socket.recv(1)
            if len(data) > 0:
                # Process received data
                print(f"Received data from {self.host}:{self.port}: {data.hex()}")
                pass

        except Exception as e:
            print(f" [PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            print(f"Handshake failed: {e}")
            # Pegamos o rastro (traceback) que está guardado dentro do 'e'
            tb = e.__traceback__
            
            # Navegamos até o último frame (onde o erro realmente aconteceu)
            while tb.tb_next:
                tb = tb.tb_next
            
            # Agora acessamos o frame e o código
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            print(f" [LOCAL] Erro no arquivo: {arquivo}, linha: {linha}")
            self.disconnect()

    def processMsg(self, msg):
        # Process the received message
        pass
    
    def keepAlive(self):
        try:

            if not self.validConnection():
                return

            print(f" [PEER] Enviando keep alive para {self.host}:{self.port}")
            self.socket.send(MsgKeepAlive().toPacket())

        except Exception as e:
            
            print(f" [PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            print(f"Handshake failed: {e}")
            # Pegamos o rastro (traceback) que está guardado dentro do 'e'
            tb = e.__traceback__
            
            # Navegamos até o último frame (onde o erro realmente aconteceu)
            while tb.tb_next:
                tb = tb.tb_next
            
            # Agora acessamos o frame e o código
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            print(f" [LOCAL] Erro no arquivo: {arquivo}, linha: {linha}")
            self.disconnect()

    def handShake(self):
        try:

            if not self.validConnection():
                return

            if not self.hasSendHandshake:
                print(f" [PEER] Enviando handshake para {self.host}:{self.port}")
                handshake_msg = MsgHandShake.ofPeer(self.peerManager.peer)
                self.socket.send(handshake_msg.toPacket())
                self.hasSendHandshake = True

            
            if not self.hasRecvHandshake:
                data = self.socket.recv(MsgHandShake.MSG_HAND_SHAKE_LENGTH)
                if len(data) == MsgHandShake.MSG_HAND_SHAKE_LENGTH:
                    recv_handshake = MsgHandShake.ofPacket(data)
                    if recv_handshake.banner == MsgHandShake.MSG_HAND_SHAKE_BANNER:
                        print(f" [PEER] Recebido handshake de {self.host}:{self.port}")
                        self.identifier = recv_handshake.identifier
                        self.feature = recv_handshake.feature
                        self.hasRecvHandshake = True

        except Exception as e:
            # Pegamos o rastro (traceback) que está guardado dentro do 'e'
            tb = e.__traceback__
            
            # Navegamos até o último frame (onde o erro realmente aconteceu)
            while tb.tb_next:
                tb = tb.tb_next
            
            # Agora acessamos o frame e o código
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            print(f" [LOCAL] Erro no arquivo: {arquivo}, linha: {linha}")

            print(f" [PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            
            print(f"Handshake failed: {e}")
            self.disconnect()

    def validConnection(self):
        if self.socket is None:
            print(f"Socket is None for {self.host}:{self.port}")
            return False

        if self.socket._closed:
            print(f"Socket is closed for {self.host}:{self.port}")
            return False

        return True    

    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.socket = None

