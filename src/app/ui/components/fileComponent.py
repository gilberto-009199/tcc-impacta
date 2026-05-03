import logging
logger = logging.getLogger(__name__)

import flet as ft
import threading
import time

class FileComponent(ft.Container):
    def __init__(self,
                app,
                uiManager,
                fileInfo):
        
        logging.info(f"{__name__} iniciou!")
        
        self.app = app
        self.uiManager = uiManager

        self.fileInfo = fileInfo
        self.name = self.fileInfo.get('name')
        self.bytes_total = self.fileInfo.get('size')

        self.bytes_download = self.fileInfo.get('bytes_download')
        self.bytes_upload = self.fileInfo.get('bytes_upload')

        self.total_pares = self.bytes_upload = self.fileInfo.get('total_pares')
        
        self.progresso = 0.0
        self.velocidade = 0
        
        self.format_bytes = self._format_bytes
        
        # Criar controles que serão atualizados
        self.progress_bar = ft.ProgressBar(value=0, height=10, border_radius=5, color=ft.Colors.BLUE)
        self.progress_text = ft.Text("0%", size=12, weight=ft.FontWeight.BOLD)
        self.download_text = ft.Text(self.format_bytes(0), size=14, weight=ft.FontWeight.BOLD)
        self.upload_text = ft.Text(self.format_bytes(0), size=14, weight=ft.FontWeight.BOLD)
        self.bytes_transferidos_text = ft.Text("0 B", size=11, weight=ft.FontWeight.BOLD)
        self.velocidade_text = ft.Text("0 MB/s", size=10, color=ft.Colors.GREY_600)
        
        super().__init__(
            content=self.criar_card(),
            margin=ft.margin.all(8),
            expand=True
        )
        
    
    def _format_bytes(self, bytes):
        for unidade in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unidade}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"
    
    def criar_card(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Cabeçalho
                    ft.Row([
                        ft.Icon(ft.Icons.INSERT_DRIVE_FILE, color=ft.Colors.BLUE, size=24),
                        ft.Text(self.name, size=16, weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.PAUSE_CIRCLE,
                            icon_color=ft.Colors.ORANGE,
                            on_click=self.toggle_pause
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=ft.Colors.RED,
                            on_click=self.cancelar
                        ),
                    ], spacing=10),
                    
                    # Estatísticas em 3 colunas
                    ft.Row([
                        # Download
                        ft.Container(
                            content=ft.Column([
                                ft.Text("DOWNLOAD", size=10, color=ft.Colors.GREY_600),
                                ft.Row([
                                    ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.GREEN, size=14),
                                    self.download_text,
                                ], spacing=3),
                            ], spacing=2),
                            expand=True
                        ),
                        
                        # Upload
                        ft.Container(
                            content=ft.Column([
                                ft.Text("UPLOAD", size=10, color=ft.Colors.GREY_600),
                                ft.Row([
                                    ft.Icon(ft.Icons.ARROW_UPWARD, color=ft.Colors.ORANGE, size=14),
                                    self.upload_text,
                                ], spacing=3),
                            ], spacing=2),
                            expand=True
                        ),
                        
                        # Pares
                        ft.Container(
                            content=ft.Column([
                                ft.Text("PARES", size=10, color=ft.Colors.GREY_600),
                                ft.Row([
                                    ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.PURPLE, size=14),
                                    ft.Text(str(self.total_pares), size=14, weight=ft.FontWeight.BOLD),
                                ], spacing=3),
                            ], spacing=2),
                            expand=True
                        ),
                    ], spacing=5),
                    
                    ft.Divider(height=1),
                    
                    # Progresso
                    ft.Column([
                        ft.Row([
                            ft.Text("Progresso", size=11, color=ft.Colors.GREY_600),
                            ft.Row([
                                self.bytes_transferidos_text,
                                ft.Text(f"/ {self.format_bytes(self.bytes_total)}", size=11),
                            ], spacing=2),
                            self.progress_text,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        self.progress_bar,
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.SPEED, size=12, color=ft.Colors.GREY_600),
                                self.velocidade_text,
                            ], spacing=2),
                            ft.Container(expand=True),
                            ft.Text("Ativo", size=10, color=ft.Colors.GREEN),
                        ]),
                    ], spacing=5),
                    
                ], spacing=12),
                padding=ft.padding.all(15),
            ),
            elevation=3,
        )
    
    def toggle_pause(self, e):
        print(f"Pausar/Resumir: {self.name}")
    
    def cancelar(self, e):
        print(f"Cancelar: {self.name}")