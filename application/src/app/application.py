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
        self.uiManager = UIManager(self)
        self.ssdpManager = SSDPManager(self)
        self.upnpManager = UPNPManager(self)
        self.peerManager = PeerManager(self)
        self.fileManager = FileManager(self)

    def config(self):
        logging.info(f"{__name__} config iniciado!")
        self.upnpManager.config()
        self.ssdpManager.config()
        self.peerManager.config()
        self.fileManager.config()
        self.uiManager.config()

    def run(self):
        logging.info(f"{__name__} run iniciado!")
        self.uiManager.run()