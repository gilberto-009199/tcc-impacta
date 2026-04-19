import logging
import random
import secrets

logger = logging.getLogger(__name__)

from reactivex.subject import BehaviorSubject

class AppData():
    
    def __init__(self):
        logging.info(f"{__name__} iniciou!")
        self.user = BehaviorSubject({
            "online": False,
            "service": False,
            "upnp": False,
            "identifier": secrets.token_bytes(160),
            "feature": [0, 0, 0]
        })
        self.network = BehaviorSubject({
            "ipLocal": False,
            "ipExternal": False,
            'port': random.randint(10000, 65535)
        })

        self.macketits = BehaviorSubject([])
        self.peers = BehaviorSubject({})

    def getData(self):
        return self
    
    def setData(self, old, newData):
        oldData = old.value
        new_data = {**oldData, **newData}
        old.on_next(new_data)
