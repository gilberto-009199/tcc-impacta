import logging
logger = logging.getLogger(__name__)

import flet as ft

class PeerComponent(ft.Container):
    def __init__(self, app, uiManager):

        logging.info(f"{__name__} iniciou!")
        
        self.app = app
        self.uiManager = uiManager

        super().__init__(
            content=ft.Column([
                
            ])
        )

        