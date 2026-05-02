import logging
logger = logging.getLogger(__name__)

import flet as ft
import flet_map as fm

from app.ui.page.homePage import HomePage
from app.ui.page.settingsPage import SettingsPage
from app.ui.page.peerPage import PeerPage

class Layout:
    def __init__(self, page: ft.Page, app, uiManager):
        
        logging.info(f"{__name__} iniciou!")
        
        self.app = app
        self.page = page
        self.uiManager = uiManager
        
        
        self.sidebar = ft.Container(
            content=ft.Column(
                controls=[
                    # pages
                    ft.Column([
                        ft.IconButton(
                            icon=ft.Icons.DOWNLOAD,
                            on_click=lambda: self.navigateTo("home"),
                            tooltip="Tela inicial"
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ROUTE,
                            on_click=lambda: self.navigateTo("peer"),
                            tooltip="Pares"
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            on_click=lambda: self.navigateTo("settings"),
                            tooltip="Configuraçoes"
                        )
                    ], tight=True),
                    # bootom
                    ft.Column([
                        ft.IconButton(
                            icon=ft.Icons.NIGHTLIGHT, 
                            on_click=self.toggle_theme,
                            tooltip="Alternar Tema"
                        )
                    ])
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=ft.Colors.SECONDARY_CONTAINER,
            padding=4,
            expand=0
        )

        self.routes = {
            "home": HomePage(app, uiManager, page),
            "settings": SettingsPage(app, uiManager, page),
            "peer": PeerPage(app, uiManager, page)
        }

        self.content = ft.Container(
            content=self.routes["home"],
            expand=4,
            padding=2,
        )

        self.mainLayout = ft.Row(
            controls=[
                self.sidebar,
                self.content
            ],
            expand=True,
            spacing=0,
        )
        
        page.add(self.mainLayout)
        

    def navigateTo(self, route):
        if route in self.routes:
            self.content.content = self.routes[route]
            self.content.update()
        else:
            logger.info(f"{__name__} route not exist {route}")

    def toggle_theme(self, e):
        # Inverte o tema atual
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
        
        self.page.update()
    def getSidebar(self):
        return self.sidebar
    
    def getContent(self):
        return self.content