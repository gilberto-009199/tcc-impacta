import logging
logger = logging.getLogger(__name__)

import flet as ft

class WelcomePage(ft.Container):
    def __init__(self, app, uiManager, page):

        logging.info(f"{__name__} iniciou!")

        self.app = app
        self.uiManager = uiManager

        super().__init__(
            content=ft.Column([
                ft.Text("Settings Principal", size=30, weight="bold"),
                ft.Text("Bem-vindo ao sistema!"),
                ft.Row([
                    ft.Container(content=ft.Text("Card 1"), bgcolor="blue", padding=20, expand=True),
                    ft.Container(content=ft.Text("Card 2"), bgcolor="green", padding=20, expand=True),
                ])
            ]),
            expand=True
        )