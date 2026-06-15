import logging
logger = logging.getLogger(__name__)

from app.util.IPUtil import IPUtil
from app.upnp.network.service import UPNPService


class UPNPManager():    
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app
        
        self.UPNPService = UPNPService(app)
        self.UPNPService.config()

        data = app.appData.getData()
        data.user.subscribe(on_next=lambda val: self.config())
        

    def config(self):
        logging.info(f"{__name__} config iniciado!")
        
        data = self.app.appData.getData()
        user = data.user.value

        if not user.get("online"):
            self.UPNPService.closePort()
            return;
        if not user.get("upnp"):
            self.UPNPService.closePort()
            return;

        self.UPNPService.config()
        self.UPNPService.openPort()

    def stop(self):
        logging.info(f"{__name__} stop iniciado!")
        self.UPNPService.closePort()
