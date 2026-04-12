from rx import Observable, Subject

class AppData():
    def __init__(self):
        self.data = Subject()
