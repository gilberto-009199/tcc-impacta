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
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.settimeout(30)
        soc.bind((
            self.host,
            self.port
        ))
        soc.listen(8)
        print(f"[SERVIDOR] Escutando em {self.host}:{self.port}...")
        while True:
            try:
                time.sleep(0.1) 
                self.appendPeers(soc) 
                time.sleep(0.1) 
                self.runPeers()
            except Exception as e:
                print(f"[SERVIDOR] Erro ao executar peers: {e}")

    def appendPeers(self, soc):
        try:
            conn, (host, port) = soc.accept()
            print(f"[SERVIDOR] Conexão recebida de {host}:{port}")
            if conn is not None:
                conn.settimeout(30)
                self.connect(conn, host, port)
        except Exception as e:
            print(f"[SERVIDOR] Erro ao conectar peer {host}:{port}: {e}")

    def runPeers(self):
        for peer in self.peers:
            try:
                print(f"[SERVIDOR] Conectado a {peer.host}:{peer.port}, logs:")
                time.sleep(0.1)        
                if not peer.run():
                    self.peerManager.removePeer(peer)
                    self.peers.remove(peer)
                
            except Exception as e:
                print(f"[SERVIDOR] Erro ao executar peer {peer.host}:{peer.port}: {e}")
                self.peerManager.removePeer(peer)
                self.peers.remove(peer)

    def connect(self, s, host, port):
        
        peer = Peer(s, host, port, self.peerManager)

        self.peerManager.createPeer(peer)
        self.peers.append(peer)

        print(f"[SERVIDOR] Novo peer conectado: {host}:{port}")


