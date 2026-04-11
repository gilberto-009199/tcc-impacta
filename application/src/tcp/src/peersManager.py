import time

from tcp.src.protocol.server import Server
from tcp.src.protocol.client import Client
from tcp.src.protocol.peer import Peer

class PeerManager:
    def __init__(self, 
                 app,
                 feedback,
                 peer = Peer(None, "192.168.0.113", 8888, None)):
        
        print(f"{__name__} Criado")

        self.server = Server(peerManager=self)
        self.client = Client(peerManager=self)
        self.peer = peer
        self.feedback = feedback
        self.peers = []
        self.app = app

    def createPeer(self, peer):
        self.peers.append(peer);

    def removePeer(self, peer):
        self.peers.remove(peer);

    def run(self, page):

        self.server.run(page);
        
        time.sleep(5)

        self.client.run(page);

        page.update()
