import logging

logger = logging.getLogger(__name__)

from app.util.IPUtil import IPUtil

from app.peer.protocol.server import Peer, Server
from app.peer.protocol.client import Client

class PeerManager():
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app
        self.server = Server(peerManager=self)
        self.clients = []

        data = app.appData.getData()
        data.user.subscribe(on_next=lambda val: self.config())

    def config(self):
        logging.info(f"{__name__} config iniciado!")
        
        if(hasattr(self.app,'fileManager')): 
            self.fileManager = self.app.fileManager

        if(hasattr(self.app, 'uiManager')): 
            self.uiManager = self.app.uiManager

        data = self.app.appData.getData()
        user = data.user.value
        
        if not user.get("online"):
            self.stop()
            return;

        ipLocal = IPUtil.getLocalIP()
        ipExternal = IPUtil.getExternalIP()
        
        ips = IPUtil.getAllLocalIPs()
        ips.extend([ipLocal, ipExternal])

        self.app.appData.setData(data.network,
            {
                "ipLocal": ipLocal,
                "ipExternal": ipExternal,
                "ips": ips
            }
        )
    
        self.run()

    def createPeer(self, ip, port):
        client = Client(peerManager=self)
        client.config(host=ip, port=port)
        self.clients.append(client)
        client.run()

    def removePeer(self, peer):
        
        if peer in self.clients:
            index =  self.clients.index(peer)
            client = self.clients[index]
            client.stop()
            if len(self.clients) > index:
                try:
                    self.clients.remove(client)
                    self.clients.pop(index)
                except Exception as e:
                    logger.info(f"[PEER MANAGER] Erro ao remover cliente: {e}")

        if peer in self.server.peers:
            self.server.removePeer(peer)
        
        peers = self.app.appData.peers.value
        for p in peers:
            if p.get("identifier") == peer.get("identifier"):
                peers.remove(p)
                break
        self.app.appData.peers.on_next(peers)


    def run(self):
        logging.info(f"{__name__} run iniciado!")
        self.server.run()
        for client in self.clients:
            client.run()
    
    def stop(self):
        logging.info(f"{__name__} stop iniciado!")

        self.server.stop()

        for client in self.clients:
            client.stop()

        self.clients = []

    def addDownloadFile(self, peer, file, path):
        logging.info(f"{__name__} addDownloadFile iniciado! peer={peer}, file={file}, path={path}")
        # avisar o filemanager
        self.fileManager.addFileDownload(file, path)
        # adicionar as menssagens de request das partes
        pass
