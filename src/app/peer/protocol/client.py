import time
import socket
import threading

import flet as ft

from app.peer.protocol.peer import Peer
from app.peer.protocol.msg.msgPieceRequest import MsgPieceRequest

import logging

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, peerManager):
        print(f"{__name__} Criado")
        self.peerManager = peerManager
        self.app = peerManager.app
        self.thread = None
        self.running = False
        self.socket = None

    def config(self, host, port):
        logger.info(f"[CLIENTE] Config iniciado")
        self.host = host
        self.port = port
        self.peer = Peer(None, self.host, self.port, self.peerManager, "client")

    def run(self):
        if self.running:
            logger.info(f"[CLIENTE] Já está rodando")
            return
        self.thread = threading.Thread(target=self.connect, daemon=True)
        self.thread.start()

    def connect(self):    
        
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        soc.connect((
            self.host,
            self.port
        ))
        
        logger.info(f"28 [CLIENTE] Conectado a {self.host}:{self.port}...")
        
        soc.settimeout(30)
        soc.setblocking(False)
        self.socket = soc
        self.peer.setSocket(soc)

        self.running = True
        
        logger.info(f"36 [CLIENTE] Conectado a {self.host}:{self.port}, logs:")

        while self.running:
            try:

                time.sleep(0.3)        
                if not self.peer.run():
                    self.peerManager.removePeer(peer=self.peer)
                    break
                
            except Exception as e:
                logger.info(f"47 [CLIENTE] Erro ao executar peer {self.peer.host}:{self.peer.port}: {e}")
                self.peerManager.removePeer(peer=self.peer)
                break

        logger.info(f"50 [CLIENTE] Desconectado de {self.host}:{self.port}")

    def stop(self):
        logger.info(f"[CLIENTE] Stop iniciado")
        self.running = False
        
        # Fechar o peer
        try:
            self.peer.disconnect()
            peers = self.app.appData.peers.value
            for p in peers:
                if p.get("identifier") == self.peer.identifier:
                    peers.remove(p)
                    break
            self.app.appData.peers.on_next(peers)
        except Exception as e:
            logger.info(f"[CLIENTE] Erro ao fechar peer: {e}")
        
        # Fechar socket
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.info(f"[CLIENTE] Erro ao fechar socket: {e}")
        
        # Aguardar thread encerrar
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=5)
            except Exception as e:
                logger.info(f"[CLIENTE] Erro ao aguardar thread: {e}")
        
        logger.info(f"[CLIENTE] Stop finalizado")
    
    def requestPieces(self, merkle_root, index, block_size):
        logging.debug(f"{__name__} requestPieces iniciado! merkle_root={merkle_root}, index={index}, block_size={block_size}")

        if not self.running:
            return;
    
        if not self.peer.msgInfo:
            return;
    
        self.peer.msgInfo.files
        
        for file in self.peer.msgInfo.files:
            if file.get('merkle_root') == merkle_root:
                # implemente isso
                msg = MsgPieceRequest(
                    identifier_file = merkle_root,
                    identifier_piece = index,
                    identifier_index = 0,
                    buffer_length = ((index*block_size) + block_size)
                )
                self.peer.queueSend(msg)
        # parei aqui gil

    def __del__(self):
        self.stop();

    def __eq__(self, value):
        if isinstance(value, Client):
            return self.peer.host == value.peer.host and self.peer.port == value.peer.port
        
        if isinstance(value, Peer):
            return self.peer.identifier == value.identifier
        
        if hasattr(value, "identifier"):
            return self.peer.identifier == value.identifier
        
        if isinstance(value, dict) and value.get("identifier", None):
            return self.peer.identifier == value["identifier"]
        
        #if value.get("identifier", None):
        #    return self.peer.identifier == value.get("identifier", None)
        
        return False    
        
                
