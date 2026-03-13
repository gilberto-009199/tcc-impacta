from datetime import time
import socket
import threading
from src.protocol.peer import Peer 

class Client:

    def __init__(self, peerManager):
        self.peerManager = peerManager
        self.thread = None
        self.host = "0.0.0.0"
        self.port = 8080

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

            peer = Peer(s, self.host, self.port, self.peerManager);

            self.peerManager.createPeer(peer);

            while True:
                peer.run();
