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

        self.dialogUpload = ft.AlertDialog(
            title=ft.Text(f"Upload: ", size=18, weight=ft.FontWeight.BOLD),
            content=[],
            actions=[
                ft.TextButton(
                    "Fechar",
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: self.close_dialog(self.dialogUpload)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=False
        )

        self.dialogDownload = ft.AlertDialog(
            title=ft.Text(f"Download: ", size=18, weight=ft.FontWeight.BOLD),
            content=[],
            actions=[
                ft.TextButton(
                    "Fechar",
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: self.close_dialog(self.dialogDownload)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=False
        )

        self.dialogQRCODE = ft.AlertDialog(
            title=ft.Text(f"QRCode: ", size=18, weight=ft.FontWeight.BOLD),
            content=[],
            actions=[
                ft.TextButton(
                    "Fechar",
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: self.close_dialog(self.dialogQRCODE)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=False
        )

        super().__init__(
            content=ft.Column([
                ft.Row([
                        self.dialogUpload,
                        self.dialogDownload,
                        self.dialogQRCODE,
                        ft.Divider(),
                        ft.Container(expand=True),
                        ft.Column([
                                ft.IconButton(
                                    icon=ft.Icons.DOWNLOAD, 
                                    icon_size=30,
                                    on_click=self.showDownloadDialog
                                ),
                                ft.Text("Download", size=10, weight=ft.FontWeight.BOLD)
                            ], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0
                        ),
                        ft.Column([
                                ft.IconButton(
                                    icon=ft.Icons.UPLOAD,
                                    icon_size=30,
                                    on_click=self.showUploadDialog
                                ),
                                ft.Text("Upload", size=10, weight=ft.FontWeight.BOLD)
                            ], 
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0
                        ),
                        ft.Column([
                                ft.IconButton(
                                    icon=ft.Icons.QR_CODE,
                                    icon_size=30,
                                    on_click=self.showQRCODEDialog
                                ),
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
                self.listFiles()
            ]),
            expand=True
        )
    

    async def showUploadDialog(self):
        
        async def pick_files(e):
            file_picker = ft.FilePicker()
            files_list = await file_picker.pick_files(allow_multiple=True)
            print("list =", files_list)
            if files_list:
                print(", ".join([f.name for f in files_list]))
            else:
                print("Cancelled!")
        
        self.dialogUpload.content = ft.Column([
            ft.Text("Em breve!"),
            ft.Button(
                "Selecionar Arquivo",
                icon=ft.Icons.UPLOAD_FILE,
                on_click=pick_files
            )
        ])
        self.dialogUpload.open = True
        self.page.update()
    
    def showDownloadDialog(self):
        self.dialogDownload.content = ft.Column([
            ft.Text("Em breve!")
        ])
        self.dialogDownload.open = True
        self.page.update()

    def showQRCODEDialog(self):
        self.dialogQRCODE.content = [
            ft.Text("Em breve!")
        ]
        self.dialogQRCODE.open = True
        self.page.update()

    def close_dialog(self, dialog):
        """Fecha o diálogo"""
        dialog.open = False
        self.page.update()

    def listFiles(self):
        return ft.Row([
            FileComponent(self.app, self.uiManager)
        ])