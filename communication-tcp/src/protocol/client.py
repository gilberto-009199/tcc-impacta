import time
import socket
import threading
from src.protocol.peer import Peer 

class Client:

    def __init__(self, peerManager):
        self.peerManager = peerManager
        self.thread = None
        self.host = "192.168.0.124"
        self.port = 8090
        self.peer = Peer(None, self.host, self.port, self.peerManager)

    def run(self):
        self.thread = threading.Thread(target=self.connect, daemon=True)
        self.thread.start()

    def connect(self):    
        
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        soc.connect((
            self.host,
            self.port
        ))
        
        print(f"[CLIENTE] Conectado a {self.host}:{self.port}...")
        
        soc.settimeout(30)

        self.peer.setSocket(soc);

        self.peerManager.createPeer(self.peer);
        
        print(f"[CLIENTE] Conectado a {self.host}:{self.port}, logs:")

        while True:
            try:

                time.sleep(0.3)        
                if not self.peer.run():
                    self.peerManager.removePeer(self.peer);
                    break

            except Exception as e:
                print(f"[CLIENTE] Erro ao executar peer {self.peer.host}:{self.peer.port}: {e}")
                self.peerManager.removePeer(self.peer);

        print(f"[CLIENTE] Desconectado de {self.host}:{self.port}")
                
