
import time
from src.protocol.peer import Peer
from src.peersManager import PeerManager
from src.protocol.client import Client
from src.protocol.server import Server

class App:
    
    def __init__(self):
        print("App intanciado")
        self.peer = Peer(None, "192.168.0.116", 8888, None)
        
        #self.peer.identifier = None
        #self.peer.feature = None
        #self.peer.port = None
        #self.peer.info = None

        self.peerManager = PeerManager(self, self.peer)
        


    def run(self):
        print("App iniciando")
        
        self.peerManager.run();        

        time.sleep(48);

        print("App finalizado")


app = App()