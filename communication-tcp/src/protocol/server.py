import socket
import threading
import time

from src.protocol.peer import Peer


class Server:

    def __init__(self, peerManager):
        self.peerManager = peerManager
        self.thread = None
        self.host = "0.0.0.0"
        self.port = 8090
        self.peers = []

    def run(self):
        self.thread = threading.Thread(target=self.serve, daemon=False)
        self.thread.start()

    def serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((
                self.host,
                self.port
            ))
            
            s.listen()
            print(f"[SERVIDOR] Escutando em {self.host}:{self.port}...")
            while True:
               try:
                    time.sleep(0.01) 
                    self.appendPeers(s)
                    time.sleep(0.02) 
                    self.runPeers()
               except Exception as e:
                    print(f"[SERVIDOR] Erro ao executar peers: {e}")

    def appendPeers(self, s):
        try:
            conn, (ip, port) = s.accept()
            print(f"[SERVIDOR] Conexão recebida de {ip}:{port}")
            with conn:                    
                conn.settimeout(30)
                self.connect(conn, ip, port)
        except Exception as e:
            print(f"[SERVIDOR] Erro ao conectar peer {ip}:{port}: {e}")

    def runPeers(self):
        for peer in self.peers:
            try:
                print(f"[SERVIDOR] Conectado a {peer.host}:{peer.port}, logs:")
                if not peer.run():
                    self.peerManager.removePeer(peer)
                    self.peers.remove(peer)
                
            except Exception as e:
                print(f"[SERVIDOR] Erro ao executar peer {peer.host}:{peer.port}: {e}")
                self.peerManager.removePeer(peer)
                self.peers.remove(peer)

    def connect(self, s, ip, port):
            
            peer = Peer(s, ip, port, self.peerManager)

            self.peerManager.createPeer(peer)
            self.peers.append(peer)

            print(f"[SERVIDOR] Novo peer conectado: {ip}:{port}")


