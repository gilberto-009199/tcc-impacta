import logging
logger = logging.getLogger(__name__)

from app.util.IPUtil import IPUtil

class UPNPManager():    
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app

        
        data = app.appData.getData()
        data.user.subscribe(on_next=lambda val: self.config())

    def config(self):
        logging.info(f"{__name__} config iniciado!")
        
        data = self.app.appData.getData()
        user = data.user.value

        if not user.get("online"):
            return;
        if not user.get("upnp"):
            return;

        pass
