import time
import socket
import threading
from src.protocol.peer import Peer 

class Client:

    def __init__(self, peerManager):
        self.peerManager = peerManager
        self.thread = None
        self.host = "127.0.0.1"
        self.port = 8090
        self.peer = Peer(None, self.host, self.port, self.peerManager)

    def run(self):
        self.thread = threading.Thread(target=self.connect, daemon=True)
        self.thread.start()

    def connect(self):    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            s.connect((
                self.host,
                self.port
            ))
            
            print(f"[CLIENTE] Conectado a {self.host}:{self.port}...")
            
            s.settimeout(30)

            self.peer.setSocket(s);

            self.peerManager.createPeer(self.peer);

            while True:
                try:

                    time.sleep(0.05) 
                    print(f"[CLIENTE] Conectado a {self.host}:{self.port}, logs:")
                    if not self.peer.run():
                        self.peerManager.removePeer(self.peer);
                        break

                except Exception as e:
                    print(f"[CLIENTE] Erro ao executar peer {self.peer.host}:{self.peer.port}: {e}")
                    self.peerManager.removePeer(self.peer);

            print(f"[CLIENTE] Desconectado de {self.host}:{self.port}")
                
