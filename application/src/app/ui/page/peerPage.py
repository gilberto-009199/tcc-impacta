import logging

logger = logging.getLogger(__name__)

import flet as ft
import flet_map as fm
import random

import time

class PeerPage(ft.Container):
    def __init__(self, app, uiManager, page):
        self.app = app
        self.uiManager = uiManager

        # Centro
        self.center = fm.MapLatitudeLongitude(-23.5505, -46.6333)
        
        # Camada de markers vazia
        self.marker_layer = fm.MarkerLayer(markers=[])
        
        self.dialog = ft.AlertDialog(
            title=ft.Text(f"Peer: ", size=18, weight=ft.FontWeight.BOLD),
            content=[],
            actions=[
                ft.TextButton(
                    "Fechar",
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: self.close_dialog(self.dialog)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=False
        )

        appData = self.app.appData
        data = appData.getData()
        user = data.user.value

        toggleOnline = ft.Switch(value=user.get('service'), label="Service Discover", on_change=lambda val: appData.setData(data.user,{ "service": val.data }))
        btnServiceDiscover = ft.Button("Find Peers", on_click=self.findPeers)

        super().__init__(
            content=ft.Column([
                    self.dialog,
                    ft.Row([
                            ft.Divider(),
                            ft.Container(expand=True),
                            btnServiceDiscover,
                            ft.Column([toggleOnline], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                            ft.Divider()
                        ], alignment=ft.MainAxisAlignment.END, spacing=32
                    ),
                    ft.Divider(),
                    fm.Map(
                        expand=True,
                        initial_center=self.center,
                        layers=[self.marker_layer]
                    )
                ],
                expand=True
            )
        )

        def reactUser(user):
            toggleOnline.value = user.get('service', False)
            page.update()
        data.user.subscribe(on_next=reactUser)
        
        

    def modalPeer(self, peer):
        """Mostra o modal com informações do peer"""
        ip, port, identifier = peer
        
        logger.info(f"Abrindo modal para: IP={ip}, Porta={port}, ID={identifier}")
        
        loading = ft.ProgressRing(visible=False, width=20, height=20)
        connect_button = ft.ElevatedButton(
            "Conectar",
            icon=ft.Icons.CONNECT_WITHOUT_CONTACT,
            on_click=lambda e: self.connect_to_peer(ip, port, loading, connect_button, self.dialog)
        )

        # Abre o diálogo
        self.dialog.content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.GREEN, size=30),
                ft.Text(f"Peer {ip}", size=18, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Divider(),
            
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DNS, color=ft.Colors.BLUE),
                title=ft.Text("IP Address", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(ip, selectable=True),
            ),
            
            ft.ListTile(
                leading=ft.Icon(ft.Icons.POWER_INPUT, color=ft.Colors.ORANGE),
                title=ft.Text("Porta", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(str(port)),
            ),
            
            ft.ListTile(
                leading=ft.Icon(ft.Icons.QR_CODE_SCANNER, color=ft.Colors.PURPLE),
                title=ft.Text("Identificador", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(str(identifier)),
            ),
            
            ft.Divider(),
            
            # Botão de conectar com loading
            ft.Container(
                content=ft.Row([
                    loading,
                    connect_button,
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                padding=ft.padding.all(10),
            ),
            
            ft.Row([
                ft.TextButton(
                    "Copiar IP",
                    icon=ft.Icons.COPY,
                    on_click=lambda e: self.copy_to_clipboard(ip)
                )
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
        ], spacing=10, tight=True)
        
        self.dialog.open = True
        self.page.update()
        
        logger.info("Modal atualizado na página")

    def connect_to_peer(self, ip, port, loading, button, dialog):
        """Tenta conectar ao peer"""
        
        # Mostra loading e desabilita botão
        loading.visible = True
        button.disabled = True
        button.text = "Conectando..."
        self.page.update()
        
        
        try:

            time.sleep(2)
            self.app.peerManager.createPeer(ip, port)

            # Fecha o modal após conectar
            dialog.open = False
            self.page.update()
            
        except Exception as e:
            # Erro na conexão
            logger.error(f"Erro ao conectar: {e}")
            
            loading.visible = False
            button.disabled = False
            button.text = "Conectar"
            self.page.update()
        
    def close_dialog(self, dialog):
        """Fecha o diálogo"""
        dialog.open = False
        self.page.update()

    def copy_to_clipboard(self, text):
        """Copia texto para área de transferência"""
        self.page.set_clipboard(text)
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"✅ IP {text} copiado!"),
                duration=2000
            )
        )

    async def findPeers(self):
        
        services = await self.app.ssdpManager.findPeers()
        print(f"Services: {services}")
        
        markers = []
        positions = [] 
        
        MIN_DISTANCE = 0.008  # ~800 metros
        
        def calculate_distance(lat1, lon1, lat2, lon2):
            """Calcula distância aproximada entre duas coordenadas em graus"""
            return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
        
        def is_too_close(lat, lon, existing_positions):
            """Verifica se a nova posição está muito próxima de alguma existente"""
            for pos in existing_positions:
                if calculate_distance(lat, lon, pos[0], pos[1]) < MIN_DISTANCE:
                    return True
            return False
        
        def find_valid_position(existing_positions, max_attempts=50):
            """Tenta encontrar uma posição válida que não colida com outras"""
            for _ in range(max_attempts):
                lat = self.center.latitude + random.uniform(-0.05, 0.05)
                lon = self.center.longitude + random.uniform(-0.05, 0.05)
                
                if not is_too_close(lat, lon, existing_positions):
                    return (lat, lon)
            
            # Se não encontrar após várias tentativas, usa a última posição mesmo assim
            lat = self.center.latitude + random.uniform(-0.05, 0.05)
            lon = self.center.longitude + random.uniform(-0.05, 0.05)
            return (lat, lon)
        
        for peer in services:
            ip, port, identifier = peer
            
            # Encontra uma posição válida
            lat, lon = find_valid_position(positions)
            positions.append((lat, lon))
            
            # Cria o marker
            markers.append(
                fm.Marker(
                    width=128,
                    height=48,
                    expand=True,
                    coordinates=fm.MapLatitudeLongitude(lat, lon),
                    content=ft.GestureDetector(
                        on_tap=lambda x, ip=ip, port=port, identifier=identifier: self.modalPeer((ip, port, identifier)),
                        content=ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.GREEN, size=16),
                                    ft.Text(f"{ip}:{port}\n{identifier}", size=8, weight=ft.FontWeight.BOLD)
                                ],
                                spacing=5,
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            bgcolor=ft.Colors.WHITE,
                            border_radius=3,
                            padding=ft.padding.all(5),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=5,
                                color=ft.Colors.BLACK
                            )
                        )
                    )   
                )
            )
    
        self.marker_layer.markers = markers
        self.marker_layer.update()
    