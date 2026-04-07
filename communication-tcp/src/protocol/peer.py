from email import header
import struct
import time

from src.protocol.msg.msgPieceRequest import MsgPieceRequest
from src.protocol.msg.msgPiece import MsgPiece
from src.protocol.msg.msgInfoRequest import MsgInfoRequest
from src.protocol.msg.msg import Msg
from src.protocol.msg.msgInfo import MsgInfo
from src.protocol.msg.msgKeepAlive import MsgKeepAlive
from src.protocol.msg.msgHandShake import MsgHandShake


class Peer:
    
    def __init__(self, socket, host, port, peerManager, name = "peer"):
        self.name = name
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
        if current_time - self.timeKeepAlive >= 24:
            print(f"{self.name}[PEER] Registrando keep alive para {self.host}:{self.port}")
            self.timeKeepAlive = current_time
            self.keepAlive()
            return True

        if current_time - self.timeSendMsgTest >= 12:
            #self.queueSend(MsgInfo())
            #self.queueSend(MsgInfoRequest())
            #self.queueSend(MsgPiece())
            #self.queueSend(MsgPieceRequest())
            self.timeSendMsgTest = current_time

        self.sendMsg();
    
        self.recvMsg();
    
        return True

    def sendMsg(self):
        
        if not self.validConnection():
            return
        
        while len(self.queueMsgSend) > 0:
            try:

                if not self.validConnection():
                    return
                
                msg = self.queueMsgSend.pop(0)
                
                
                packet = msg.toPacket()
                print(f"{self.name}[PEER] ENVIANDO MENSSAGEM DE {msg.__class__.__name__} para {self.host}:{self.port}")
                print(f"""\t + HEADER: {packet[0:2].hex()} (type: {packet[0]}, length: {packet[1]})""")
                print(f"\t + BUFFER: {packet[2:].hex()}")

                self.socket.send(packet)

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

            header = self.socket.recv(3)

            if len(header) < 3:
                raise Exception("Header incompleto")

            msg_type, payload_len = struct.unpack('!BH', header)

            print(f"{self.name}[PEER] Recebido header from {self.host}:{self.port}: {header.hex()}")
            print(f"{self.name}[PEER] + type: {msg_type}")
            print(f"{self.name}[PEER] + length: {payload_len}")

            buffer = header + self.socket.recv(payload_len)
            self.processMsg(msg_type, payload_len, buffer)

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

    def processMsg(self, msg_type, payload_len, buffer):
        
        print(f"{self.name}[PEER] Recebeu:")

        match msg_type:
            case Msg.MSG_TYPE_KEEP_ALIVE:
                print(f"{self.name}[PEER] Recebido keep alive de {self.host}:{self.port}")
                print(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                print(f"\t + BUFFER: {buffer.hex()}")
                data = MsgKeepAlive.ofPacket(buffer);
                print(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_PIECE_REQUEST:
                print(f"{self.name}[PEER] Recebido piece request de {self.host}:{self.port}")
                print(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                print(f"\t + BUFFER: {buffer.hex()}")
                data = MsgPieceRequest.ofPacket(buffer);
                print(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_INFO:
                print(f"{self.name}[PEER] Recebido info de {self.host}:{self.port}")
                print(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                print(f"\t + BUFFER: {buffer.hex()}")

                data = MsgInfo.ofPacket(buffer);
                print(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_INFO_REQUEST:
                print(f"{self.name}[PEER] Recebido info request de {self.host}:{self.port}")
                print(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                print(f"\t + BUFFER: {buffer.hex()}")

                data = MsgInfoRequest.ofPacket(buffer);
                print(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_HAND_SHAKE:
                print(f"{self.name}[PEER] Recebido handshake de {self.host}:{self.port}")
                print(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                print(f"\t + BUFFER: {buffer.hex()}")

                data = MsgHandShake.ofPacket(buffer);
                print(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_PIECE:
                print(f"{self.name}[PEER] Recebido piece de {self.host}:{self.port}")
                print(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                print(f"\t + BUFFER: {buffer.hex()}")

                data = MsgPiece.ofPacket(buffer);
                print(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_PIECE_REQUEST:
                print(f"{self.name}[PEER] Recebido piece request de {self.host}:{self.port}")
                print(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                print(f"\t + BUFFER: {buffer.hex()}")

                data = MsgPieceRequest.ofPacket(buffer);
                print(f"\t + MSG : {data}")

            case _:
                print(f"{self.name}[PEER] Recebido msg desconhecida de {self.host}:{self.port}")
                print(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                print(f"\t + BUFFER: {buffer.hex()}")
                data = Msg.ofPacket(buffer);
                print(f"\t + MSG : {data}")

    def keepAlive(self):
        try:

            if not self.validConnection():
                return

            print(f"{self.name}[PEER] Enviando keep alive para {self.host}:{self.port}:")
            packet = MsgKeepAlive().toPacket()
            self.socket.send(packet)
            
            msg_type, payload_len = struct.unpack('!BH', packet[0:3])

            print(f"{self.name}[PEER] Enviado header do keep alive de {self.host}:{self.port}: {packet.hex()}")
            print(f"{self.name}[PEER] + type: {msg_type}")
            print(f"{self.name}[PEER] + length: {payload_len}")

        except Exception as e:
            
            print(f" {self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            print(f"keepAlive failed: {e}")
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

            
            if not self.validConnection():
                return
            
            if not self.hasRecvHandshake:
                header = self.socket.recv(3)
                
                if len(header) < 3:
                    return
                
                msg_type, payload_len = struct.unpack('!BH', header)

                buffer = self.socket.recv(payload_len)
                if msg_type == Msg.MSG_TYPE_HAND_SHAKE:
                    packet = header + buffer
                    recv_handshake = MsgHandShake.ofPacket(packet)
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
            print(f"{self.name}[PEER] Erro no arquivo: {arquivo}, linha: {linha}")

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

    def __eq__(self, other):
        
        if not isinstance(other, Peer):
            return False
        
        return (
            self.host == other.host
        and 
            self.port == other.port
        and
            self.identifier == other.identifier
        )