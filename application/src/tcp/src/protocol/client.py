import time
import socket
import threading

import flet as ft

from tcp.src.protocol.peer import Peer 

import logging

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, peerManager):
        print(f"{__name__} Criado")
        self.peerManager = peerManager
        self.thread = None
        self.host = "192.168.0.116"
        self.port = 8888
        self.peer = Peer(None, self.host, self.port, self.peerManager, "client")

    def run(self, page):
        self.page = page
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
        self.peer.setSocket(soc);

        self.peerManager.createPeer(self.peer);
        
        logger.info(f"36 [CLIENTE] Conectado a {self.host}:{self.port}, logs:")

        while True:
            try:

                time.sleep(0.3)        
                if not self.peer.run():
                    self.peerManager.removePeer(peer=self.peer)
                    break
                
                self.page.update()
                
            except Exception as e:
                logger.info(f"47 [CLIENTE] Erro ao executar peer {self.peer.host}:{self.peer.port}: {e}")
                self.peerManager.removePeer(peer=self.peer)
                break

        logger.info(f"50 [CLIENTE] Desconectado de {self.host}:{self.port}")
                
