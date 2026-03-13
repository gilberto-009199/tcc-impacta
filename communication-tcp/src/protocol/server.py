import socket
import threading

from src.protocol.peer import Peer


class Server:

    def __init__(self, peerManager):
        self.peerManager = peerManager
        self.thread = None
        self.host = "0.0.0.0"
        self.port = 8080
        

    def run(self):
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((
                self.host,
                self.port
            ))
            s.listen()
            print(f"[SERVIDOR] Escutando em {self.host}:{self.port}...")
            
            conn, (ip, port) = s.accept()
            with conn:
                while True:
                    self.connect(conn, ip, port);

    def connect(self, s, ip, port):
            
            peer = Peer(s, ip, port, self.peerManager);

            self.peerManager.createPeer(peer);

            while True:
                peer.run();
