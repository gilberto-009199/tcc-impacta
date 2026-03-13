import src.protocol.server as Server
import src.protocol.client as Client
from src.protocol.peer import Peer

class PeerManager():

    def __init__(self, app):
        self.peers = []
        self.app = app
        
    def createPeer(self, peer):
        self.peers.append(peer);
        return peer;

    def run(self):
        self.server = Server(self);
        self.client = Client(self);
        
        self.server.run();
        self.client.run();
