from email import header
import time

from src.protocol.msg.msg import Msg
from src.protocol.msg.msgInfo import MsgInfo
from src.protocol.msg.msgKeepAlive import MsgKeepAlive
from src.protocol.msg.msgHandShake import MsgHandShake


class Peer:
    
    def __init__(self, socket, host, port, peerManager, name = "peer"):
        self.name = name;
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
        self.timeSendMsgTest = 0;

        self.queueMsgRecv = []
        self.queueMsgSend = []

    def setSocket(self, socket):
        self.socket = socket;
    
    def queueSend(self, msg):
        self.queueMsgSend.append(msg);

    def queueRecv(self, msg):
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
        if current_time - self.timeKeepAlive >= 10:
            print(f"{self.name}[PEER] Enviando keep alive para {self.host}:{self.port}")
            self.timeKeepAlive = current_time
            self.keepAlive()
            return True

        self.sendMsg();
    
        self.recvMsg();
        
        current_time = time.time()
        if current_time - self.timeSendMsgTest >= 4:
            print(f"{self.name}[PEER] Enviando MSG info para {self.host}:{self.port}")
            
            self.queueSend(MsgInfo())
            self.timeSendMsgTest = current_time

        return True

    def sendMsg(self):
        
        while len(self.queueMsgSend) > 0:
            try:
                msg = self.queueMsgSend.pop(0)
                if self.validConnection():
                    return
                
                print(f"{self.name}[PEER] ENVIANDO MENSSAGEM DE {msg.__class__.__name__}, Payload: {msg.toPacket().hex()}")
                self.socket.send(msg.toPacket())

            except BlockingIOError:
                pass
            except Exception as e:
                print(f"{self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
                print(f"{self.name}[PEER] failed: {e}")
                self.disconnect()

    def recvMsg(self):
        try:
            if not self.validConnection():
                return

            header = self.socket.recv(2)
            if len(header) > 0:
                print(f"{self.name}[PEER] Recebido header from {self.host}:{self.port}: {header.hex()}")
                buffer = self.socket.recv(header[1])
                self.processMsg(header, buffer)

        except BlockingIOError:
            pass
        except Exception as e:
            print(f"{self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            print(f"{self.name}[PEER] failed: {e}")
            # Pegamos o rastro (traceback) que está guardado dentro do 'e'
            tb = e.__traceback__
            
            # Navegamos até o último frame (onde o erro realmente aconteceu)
            while tb.tb_next:
                tb = tb.tb_next
            
            # Agora acessamos o frame e o código
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            print(f"{self.name}[PEER] [LOCAL] Erro no arquivo: {arquivo}, linha: {linha}")
            self.disconnect()

    def processMsg(self, header, buffer):
        
        print(f"{self.name}[PEER] Recebeu")
        print(f" + HEADER: {header.hex()}")
        print(f" + BUFFER: {buffer.hex()}")

        match header[0]:
            case Msg.MSG_TYPE_KEEP_ALIVE:
                print(f"{self.name}[PEER] Recebido keep alive de {self.host}:{self.port}")
            case Msg.MSG_TYPE_PIECE_REQUEST:
                print(f"{self.name}[PEER] Recebido piece request de {self.host}:{self.port}")
            case Msg.MSG_TYPE_INFO:
                print(f"{self.name}[PEER] Recebido info de {self.host}:{self.port}")
            case _:
                print(f"{self.name}[PEER] Recebido msg desconhecida de {self.host}:{self.port}: {header.hex()}")

    
    def keepAlive(self):
        try:

            if not self.validConnection():
                return

            print(f"{self.name}[PEER] Enviando keep alive para {self.host}:{self.port}")
            self.socket.send(MsgKeepAlive().toPacket())

        except Exception as e:
            
            print(f" {self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
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
                print(f"{self.name}[PEER] Enviando handshake para {self.host}:{self.port}")
                handshake_msg = MsgHandShake.ofPeer(self.peerManager.peer)
                self.socket.send(handshake_msg.toPacket())
                self.hasSendHandshake = True

            
            if not self.hasRecvHandshake:
                data = self.socket.recv(MsgHandShake.MSG_HAND_SHAKE_LENGTH)
                if len(data) == MsgHandShake.MSG_HAND_SHAKE_LENGTH:
                    recv_handshake = MsgHandShake.ofPacket(data)
                    if recv_handshake.banner == MsgHandShake.MSG_HAND_SHAKE_BANNER:
                        print(f"{self.name}[PEER] Recebido handshake de {self.host}:{self.port}")
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

            print(f"{self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            
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

