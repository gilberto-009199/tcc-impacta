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
        ft.run(self.gui)

    def gui(self, page: ft.Page):
        logging.info(f"{__name__} gui iniciado!")
        self.page = page
        self.page.title = "P2P"
        self.page.padding = 0
        self.page.margin = 0
        self.layout = Layout(page=page,app=self.app, uiManager=self)

"""
        data = self.app.appData.getData()
        networkData = data.network

        text_ip_local = ft.Text(f"IP Local: {networkData.value.get('ipLocal', '...')}", size=16)
        text_ip_external = ft.Text(f"IP Externo: {networkData.value.get('ipExternal', '...')}", size=16)
        
        networkData.subscribe(
            on_next=lambda val: (
                setattr(text_ip_local, "value", val.get("ipLocal")),
                setattr(text_ip_external, "value", val.get("ipExternal")),
                self.page.update()
            )
        )

        self.page.add(
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Informações de Rede", weight="bold", size=20),
                        text_ip_local,
                        text_ip_external,
                    ]),
                    padding=20
                )
            )
        )

"""
