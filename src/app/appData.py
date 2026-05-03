import base64
import logging
import random
import secrets
import os
from pathlib import Path

logger = logging.getLogger(__name__)

from reactivex.subject import BehaviorSubject

class AppData():
    
    def __init__(self):
        logging.info(f"{__name__} iniciou!")
        self.user = BehaviorSubject({
            "online": False,
            "service": False,
            "upnp": False,
            "identifier": base64.b64encode(secrets.token_bytes(160)).decode('utf-8'),
            "feature": [0, 0, 0],
            "download": os.path.join(str(Path.home()), "Downloads")
        })
        self.network = BehaviorSubject({
            "ipLocal": False,
            "ipExternal": False,
            'port': random.randint(10000, 65535)
        })

        self.files = BehaviorSubject([

        ])
        self.peers = BehaviorSubject([

        ])

    def getData(self):
        return self
    
    def setData(self, old, newData):
        oldData = old.value
        
        if isinstance(oldData, dict) and isinstance(newData, dict):
            new_data = {**oldData, **newData}
        elif isinstance(oldData, list) and isinstance(newData, list):
            new_data = oldData + newData
        else:
            new_data = newData

        old.on_next(new_data)
