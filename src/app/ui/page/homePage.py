import logging
logger = logging.getLogger(__name__)

import flet as ft

from app.ui.components.fileComponent import FileComponent 

class HomePage(ft.Container):
    def __init__(self, app, uiManager, page):

        logging.info(f"{__name__} iniciou!")
        
        self.app = app
        self.uiManager = uiManager

        appData = self.app.appData
        data = appData.getData()
        user = data.user.value

        toggleOnline = ft.Switch(value=user.get('online'), label="Online", on_change=lambda val: appData.setData(data.user,{ "online": val.data }))

        def reactUser(data):
            toggleOnline.value = data.get('online')
        data.user.subscribe(on_next=reactUser)

        super().__init__(
            content=ft.Column([
                ft.Row([
                        ft.Divider(),
                        ft.Container(expand=True),
                        ft.Column([
                                ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_size=30),
                                ft.Text("Download", size=10, weight=ft.FontWeight.BOLD)
                            ], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0
                        ),
                        ft.Column([
                                ft.IconButton(icon=ft.Icons.UPLOAD, icon_size=30),
                                ft.Text("Upload", size=10, weight=ft.FontWeight.BOLD)
                            ], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0
                        ),
                        ft.Column([
                                ft.IconButton(icon=ft.Icons.QR_CODE, icon_size=30),
                                ft.Text("QRCode", size=10, weight=ft.FontWeight.BOLD)
                            ], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0
                        ),
                        ft.Column([
                                toggleOnline
                            ], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0
                        ),
                        ft.Divider()
                    ], 
                    alignment=ft.MainAxisAlignment.END,
                    spacing=32
                ),
                ft.Divider(),
                self.listPeers()
            ]),
            expand=True
        )
    def listPeers(self):
        return ft.Row([
            FileComponent(self.app, self.uiManager)
        ])