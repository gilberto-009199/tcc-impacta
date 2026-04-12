import logging

logger = logging.getLogger(__name__)

from app.appData import AppData
from app.ui.UIManager import UIManager
from app.upnp.UPNPManager import UPNPManager
from app.ssdp.SSDPManager import SSDPManager
from app.peer.peerManager import PeerManager
from app.file.fileManager import FileManager

class Application():
    def __init__(self):
        logging.info(f"{__name__} iniciou!")
        self.appData = AppData()
        self.ui = UIManager(self)
        self.ssdp = SSDPManager(self)
        self.upnp = UPNPManager(self)
        self.peer = PeerManager(self)
        self.file = FileManager(self)
        

    def config(self):
        logging.info(f"{__name__} config iniciado!")
        self.upnp.config()
        self.ssdp.config()
        self.peer.config()
        self.file.config()
        self.ui.config()

    def run(self):
        logging.info(f"{__name__} run iniciado!")
        self.ui.run()