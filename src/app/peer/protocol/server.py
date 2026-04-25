import random
import socket
import threading
import time

import flet as ft

from app.peer.protocol.peer import Peer

import logging

logger = logging.getLogger(__name__)

class Server:
    def __init__(self, peerManager):
        print(f"{__name__} Criado")
        logger.info(f"[SERVIDOR] Criado")
        self.peerManager = peerManager
        self.thread = None
        self.host = "0.0.0.0"
        self.port = random.randint(10000, 65535)
        self.peers = []
        self.running = False
        self.socket = None

    def run(self):
        network = self.peerManager.app.appData.network;
        self.host = network.value.get("ipLocal", self.host)
        self.port = network.value.get("port", self.port)

        if self.running:
            logger.info(f"[SERVIDOR] Já está rodando")
            return
        self.thread = threading.Thread(target=self.serve, daemon=False)
        self.thread.start()

    def serve(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.settimeout(30)
        soc.bind((
            self.host,
            self.port
        ))
        soc.listen()
        soc.setblocking(False)
        self.socket = soc
        self.running = True
        logger.info(f"[SERVIDOR] Escutando em {self.host}:{self.port}...")
        while self.running:
            try:
                time.sleep(0.1) 
                self.appendPeers(soc) 
                time.sleep(0.1) 
                self.runPeers()
            except BlockingIOError:
                pass
            except Exception as e:
                logger.info(f"41 [SERVIDOR] Erro ao executar peers: {e}")
                tb = e.__traceback__
                
                while tb.tb_next:
                    tb = tb.tb_next
                
                linha = tb.tb_lineno
                arquivo = tb.tb_frame.f_code.co_filename
                logger.info(f"48 [SERVER] Erro no arquivo: {arquivo}, linha: {linha}")

    def appendPeers(self, soc):
        try:

            conn, (host, port) = soc.accept()
            logger.info(f"53 [SERVIDOR] Conexão recebida de {host}:{port}")
            if conn is not None:
                conn.settimeout(30)
                self.connect(conn, host, port)

        except BlockingIOError:
            pass
        except Exception as e:
            logger.info(f"58 [SERVIDOR] Erro ao conectar peer novo: {e}")

    def runPeers(self):

        for peer in self.peers:
            try:
                logger.info(f"63 [SERVIDOR] Conectado a {peer.host}:{peer.port}, logs:")
                if not peer.run():
                    self.peers.remove(peer)
            except BlockingIOError:
                pass
            except Exception as e:
                logger.info(f"70 [SERVIDOR] Erro ao executar peer {peer.host}:{peer.port}: {e}")
                self.peers.remove(peer)

    def connect(self, s, host, port):
        
        peer = Peer(s, host, port, self.peerManager, "server")

        self.peers.append(peer)

        logger.info(f"81 [SERVIDOR] Novo peer conectado: {host}:{port}")

    def stop(self):
        logger.info(f"[SERVIDOR] Stop iniciado")
        self.running = False
        
        # Fechar todos os peers
        for peer in self.peers:
            try:
                peer.close()
            except Exception as e:
                logger.info(f"[SERVIDOR] Erro ao fechar peer: {e}")
        
        self.peers.clear()
        
        # Fechar socket do servidor
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.info(f"[SERVIDOR] Erro ao fechar socket: {e}")
        
        # Aguardar tema encerrar
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info(f"[SERVIDOR] Stop finalizado")


