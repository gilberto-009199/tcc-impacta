import logging

logger = logging.getLogger(__name__)

from reactivex.subject import BehaviorSubject

class AppData():
    
    def __init__(self):
        logging.info(f"{__name__} iniciou!")
        self.user = BehaviorSubject({
            "online": False,
            "service": False,
            "upnp": False
        })
        self.network = BehaviorSubject({
            "ipLocal": False,
            "ipExternal": False
        })
        self.files = BehaviorSubject([])
        self.peer = BehaviorSubject({})

    def getData(self):
        return self
    
    def setData(self, old, newData):
        oldData = old.value
        new_data = {**oldData, **newData}
        old.on_next(new_data)
