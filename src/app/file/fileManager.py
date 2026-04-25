import logging

logger = logging.getLogger(__name__)

class FileManager():
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app

    def config(self):
        logging.info(f"{__name__} config iniciado!")
        pass

    def run(self):
        logging.info(f"{__name__} run iniciado!")
        pass

    def stop(self):
        logging.info(f"{__name__} stop iniciado!")
        pass