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
        
        self.listFiles = ft.Column([self.renderlistFiles()], alignment=ft.Alignment.CENTER )
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
                self.listFiles
            ],horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True
        )
    
        def reactFiles(files):
            lista = self.renderlistFiles(files=files)
            self.listFiles.controls = lista
            page.update()
        data.files.subscribe(on_next=reactFiles)
        

    async def showUploadDialog(self):
        
        async def pick_files(e):
            file_picker = ft.FilePicker()
            files_list = await file_picker.pick_files(allow_multiple=False)

            if files_list[0]:
                file = files_list[0]
                fileInfo = self.app.fileManager.addFile(name=file.name, path=file.path)

            else:
                print("Cancelled!")
        
        self.dialogUpload.content = ft.Column([
            ft.Button(
                "Selecionar Arquivo",
                icon=ft.Icons.UPLOAD_FILE,
                on_click=pick_files
            )
        ])
        self.dialogUpload.open = True
        self.page.update()

    def close_dialog(self, dialog):
        """Fecha o diálogo"""
        dialog.open = False
        self.page.update()

    def renderlistFiles(self, files=[]):
        
        print(f"\n\n DADOS DE FILES: {files} \n\n")

        return [FileComponent(self.app, self.uiManager, fileInfo=file) for file in files] if len(files) > 0 else ft.Text("Nenhum arquivo presente",text_align= ft.TextAlign.CENTER, size=14, color=ft.Colors.GREY_600);
        