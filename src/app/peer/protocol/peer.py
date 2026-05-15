import struct
import time

import flet as ft

from app.peer.protocol.msg.msgPieceRequest import MsgPieceRequest
from app.peer.protocol.msg.msgPiece import MsgPiece
from app.peer.protocol.msg.msgInfoRequest import MsgInfoRequest
from app.peer.protocol.msg.msg import Msg
from app.peer.protocol.msg.msgInfo import MsgInfo
from app.peer.protocol.msg.msgKeepAlive import MsgKeepAlive
from app.peer.protocol.msg.msgHandShake import MsgHandShake

import logging

logger = logging.getLogger(__name__)


class Peer:
    
    def __init__(self, socket, host, port, peerManager, name = "peer"):
        print(f"{__name__} Criado")
        self.name = name
        self.socket = socket
        self.host = host
        self.port = port
        self.peerManager = peerManager
        self.app = peerManager.app
        self.msgInfo = False
        
        self.hasSendHandshake = False
        self.hasRecvHandshake = False

        self.timeKeepAlive = 0;
        self.timeSendMsgInfo = 0;

        self.queueMsgRecv = []
        self.queueMsgSend = []

    def setSocket(self, socket):
        self.socket = socket;
    
    def queueSend(self, msg):
        if msg in self.queueMsgSend:
            return
        
        self.queueMsgSend.append(msg)

    def queueRecv(self, msg):
        self.queueMsgRecv.append(msg)

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
            logger.info(f"{self.name}[PEER] Registrando keep alive para {self.host}:{self.port}")
            self.timeKeepAlive = current_time
            self.keepAlive()
            return True

        
        # UpdateInfo
        if current_time - self.timeSendMsgInfo >= 32:
            self.queueSend(MsgInfoRequest())
            self.timeSendMsgInfo = current_time

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
                logger.info(f"{self.name}[PEER] ENVIANDO MENSSAGEM DE {msg.__class__.__name__} para {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: {packet[0:2].hex()} (type: {packet[0]}, length: {packet[1]})""")
                logger.info(f"\t + BUFFER: {packet[2:].hex()}")
                

                self.socket.send(packet)
                self.timeKeepAlive = time.time()

            except BlockingIOError:
                pass
            except Exception as e:
                logger.info(f"{self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
                logger.info(f"{self.name}[PEER] failed: {e}")
                self.disconnect()

    def recvMsg(self):
        try:
            if not self.validConnection():
                return

            header = self.socket.recv(3)

            if len(header) < 3:
                raise Exception("Header incompleto")

            msg_type, payload_len = struct.unpack('!BH', header)

            logger.info(f"{self.name}[PEER] Recebido header from {self.host}:{self.port}: {header.hex()}")
            logger.info(f"{self.name}[PEER] + type: {msg_type}")
            logger.info(f"{self.name}[PEER] + length: {payload_len}")

            buffer = header + self.socket.recv(payload_len)
            self.processMsg(msg_type, payload_len, buffer)

        except BlockingIOError:
            pass
        except Exception as e:
            logger.info(f"{self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            logger.info(f"{self.name}[PEER] failed: {e}")

            # Pegamos o rastro (traceback) que está guardado dentro do 'e'
            tb = e.__traceback__
            
            # Navegamos até o último frame (onde o erro realmente aconteceu)
            while tb.tb_next:
                tb = tb.tb_next
            
            # Agora acessamos o frame e o código
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            logger.info(f"{self.name}[PEER] [LOCAL] Erro no arquivo: {arquivo}, linha: {linha}")
           
            self.disconnect()

    def processMsg(self, msg_type, payload_len, buffer):
        
        logger.info(f"{self.name}[PEER] Recebeu:")


        match msg_type:
            case Msg.MSG_TYPE_KEEP_ALIVE:
                logger.info(f"{self.name}[PEER] Recebido keep alive de {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                logger.info(f"\t + BUFFER: {buffer.hex()}")
                data = MsgKeepAlive.ofPacket(buffer);
                logger.info(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_PIECE_REQUEST:
                logger.info(f"{self.name}[PEER] Recebido piece request de {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                logger.info(f"\t + BUFFER: {buffer.hex()}")
                data = MsgPieceRequest.ofPacket(buffer);
                logger.info(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_INFO:
                logger.info(f"{self.name}[PEER] Recebido info de {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                logger.info(f"\t + BUFFER: {buffer.hex()}")

                data = MsgInfo.ofPacket(buffer);
                self.msgInfo = data
                logger.info(f"\t + MSG : {data}")
                
                appData = self.app.appData.getData()

                peers = appData.peers.value;
            
                for p in peers:
                    if p.get("identifier", None) == data.identifier:
                        p["feature"] = data.feature
                        p["files"] = data.files

                appData.peers.on_next(peers)
                    

            case Msg.MSG_TYPE_INFO_REQUEST:
                logger.info(f"{self.name}[PEER] Recebido info request de {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                logger.info(f"\t + BUFFER: {buffer.hex()}")

                data = MsgInfoRequest.ofPacket(buffer);
                logger.info(f"\t + MSG : {data}")
                appData = self.app.appData.getData()

                user = appData.user.value;
                network = appData.network.value;
                files = appData.files.value;
                peers = appData.peers.value;

                identifier = user.get("identifier", None)
                feature = user.get("feature", None)

                self.queueSend(MsgInfo(
                    feature=feature,
                    identifier=identifier,
                    files=files,
                    peers=peers
                ))

            case Msg.MSG_TYPE_HAND_SHAKE:
                logger.info(f"{self.name}[PEER] Recebido handshake de {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                logger.info(f"\t + BUFFER: {buffer.hex()}")

                data = MsgHandShake.ofPacket(buffer);
                logger.info(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_PIECE:
                logger.info(f"{self.name}[PEER] Recebido piece de {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                logger.info(f"\t + BUFFER: {buffer.hex()}")

                data = MsgPiece.ofPacket(buffer);
                logger.info(f"\t + MSG : {data}")

            case Msg.MSG_TYPE_PIECE_REQUEST:
                logger.info(f"{self.name}[PEER] Recebido piece request de {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                logger.info(f"\t + BUFFER: {buffer.hex()}")

                data = MsgPieceRequest.ofPacket(buffer);
                logger.info(f"\t + MSG : {data}")

            case _:
                logger.info(f"{self.name}[PEER] Recebido msg desconhecida de {self.host}:{self.port}")
                logger.info(f"""\t + HEADER: type: {msg_type}, length: {payload_len})""")
                logger.info(f"\t + BUFFER: {buffer.hex()}")
                data = Msg.ofPacket(buffer);
                logger.info(f"\t + MSG : {data}")
        
    def keepAlive(self):
        try:

            if not self.validConnection():
                return

            logger.info(f"{self.name}[PEER] Enviando keep alive para {self.host}:{self.port}:")
            packet = MsgKeepAlive().toPacket()
            self.socket.send(packet)
            
            msg_type, payload_len = struct.unpack('!BH', packet[0:3])

            logger.info(f"{self.name}[PEER] Enviado header do keep alive de {self.host}:{self.port}: {packet.hex()}")
            logger.info(f"{self.name}[PEER] + type: {msg_type}")
            logger.info(f"{self.name}[PEER] + length: {payload_len}")

        except Exception as e:
            
            logger.info(f" {self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            logger.info(f"keepAlive failed: {e}")
            # Pegamos o rastro (traceback) que está guardado dentro do 'e'
            tb = e.__traceback__
            
            # Navegamos até o último frame (onde o erro realmente aconteceu)
            while tb.tb_next:
                tb = tb.tb_next
            
            # Agora acessamos o frame e o código
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            logger.info(f" [LOCAL] Erro no arquivo: {arquivo}, linha: {linha}")
            self.disconnect()

    def handShake(self):
        try:

            if not self.validConnection():
                return

            if not self.hasSendHandshake:
                logger.info(f"{self.name}[PEER] Enviando handshake para {self.host}:{self.port}")
                appData = self.app.appData.getData()

                user = appData.user.value;

                identifier = user.get("identifier", None)
                feature = user.get("feature", None)

                handshake_msg = MsgHandShake.ofPeer(identifier=identifier, feature=feature)
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
                        logger.info(f"{self.name}[PEER] Recebido handshake de {self.host}:{self.port}")
                        self.identifier = recv_handshake.identifier
                        self.feature = recv_handshake.feature
                        self.hasRecvHandshake = True
                        data = self.app.appData.getData()
                        peers = data.peers.value
                        peers.append({
                            "host": self.host,
                            "port": self.port,
                            "identifier": self.identifier,
                            "feature": self.feature
                        })
                        data.peers.on_next(peers)
                        logger.info(f"{self.name}[PEER] Handshake recebido com sucesso de {self.host}:{self.port}")

        except Exception as e:
            # Pegamos o rastro (traceback) que está guardado dentro do 'e'
            tb = e.__traceback__
            
            # Navegamos até o último frame (onde o erro realmente aconteceu)
            while tb.tb_next:
                tb = tb.tb_next
            
            # Agora acessamos o frame e o código
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            logger.info(f"{self.name}[PEER] Erro no arquivo: {arquivo}, linha: {linha}")

            logger.info(f"{self.name}[PEER] Erro ao executar peer {self.host}:{self.port}: {e}")
            
            logger.info(f"Handshake failed: {e}")
            self.disconnect()

    def validConnection(self):
        if self.socket is None:
            logger.info(f"Socket is None for {self.host}:{self.port}")
            return False

        if self.socket._closed:
            logger.info(f"Socket is closed for {self.host}:{self.port}")
            return False

        return True

    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.socket = None

    def __eq__(self, value):
        
        if isinstance(value, Peer):
            return self.host == value.host and self.port == value.port
        
        if hasattr(value, "identifier"):
            return self.identifier == value.identifier
        
        if isinstance(value, dict) and value.get("identifier", None):
            return self.identifier == value["identifier"]
        
        
        return False