import logging

logger = logging.getLogger(__name__)

import flet as ft

from app.ui.layout import Layout

class UIManager():    
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app

    def config(self):
        logging.info(f"{__name__} config iniciado!")
        pass
    
    def run(self):
        logging.info(f"{__name__} run iniciado!")
        ft.run(self.gui, upload_dir=".")

    def gui(self, page: ft.Page):
        logging.info(f"{__name__} gui iniciado!")
        self.page = page
        self.page.title = "P2P"
        self.page.padding = 0
        self.page.margin = 0
        self.layout = Layout(page=page,app=self.app, uiManager=self)
        #file_picker = ft.FilePicker(on_upload=lambda e: print(e.files))
        #page.overlay.append(file_picker)
        #page.file_picker = file_picker
        
