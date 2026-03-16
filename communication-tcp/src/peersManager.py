import time

from src.protocol.server import Server
from src.protocol.client import Client
from src.protocol.peer import Peer

class PeerManager:
    def __init__(self, app, peer = None):
        self.server = Server(self)
        self.client = Client(self)
        self.peer = peer
        self.peers = []
        self.app = app

    def createPeer(self, peer):
        self.peers.append(peer);

    def removePeer(self, peer):
        self.peers.remove(peer);


    def run(self):

        self.server.run();
        
        time.sleep(5)

        self.client.run();
