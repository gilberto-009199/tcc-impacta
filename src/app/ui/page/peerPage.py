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
        self.marker_layer = fm.MarkerLayer(markers=[
            fm.Marker(
                width=128,
                height=128,
                expand=True,
                coordinates=self.center,
                content=ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.GREY, size=64),
                            ft.Text("You", size=12, weight=ft.FontWeight.BOLD)
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    bgcolor=ft.Colors.TRANSPARENT,
                    border_radius=3
                )
            )
        ])
        self.lines_layer = fm.PolylineLayer(polylines=[])

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

        # Lista de peers no canto direito
        self.peers_list = ft.ListView(
            expand=True,
            spacing=5,
            height=400,
            width=280,
            auto_scroll=True
        )
        self.peers_container = ft.Container(
            content=ft.Column([
                ft.Text("Peers Conectados", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(height=1, color=ft.Colors.GREY_400),
                self.peers_list
            ], spacing=10),
            width=300,
            height=450,
            bgcolor=ft.Colors.BLACK54,
            border_radius=10,
            padding=10,
            right=10,
            bottom=1,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.BLACK26
            )
        )

        super().__init__(
            content=ft.Stack([
                ft.Column([
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
                            layers=[self.lines_layer, self.marker_layer]
                        )
                    ],
                    expand=True
                ),
                self.peers_container
            ], expand=True)
        )

        def reactUser(user):
            toggleOnline.value = user.get('service', False)
            page.update()
        data.user.subscribe(on_next=reactUser)
        
        self.build()

        def reactPeers(peers):
           self.updateMap(services=peers)
           self.updatePeers(peers)
           page.update()
        data.peers.subscribe(on_next=reactPeers)

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
        
        if not self.marker_layer.page:
            return
        
    
        services = await self.app.ssdpManager.findPeers()
        
        services and len(services) > 0 and self.updateMap(services)

    def updateMap(self, services = []):
        try:
            # Verifica se está na página sem causar RuntimeError
            if not hasattr(self.marker_layer, 'page') or self.marker_layer.page is None:
                return
        except RuntimeError:
            return
        
        appData = self.app.appData
        data = appData.getData()
        user = data.user.value
        peers = data.peers.value

        positions = [] 
        
        MIN_DISTANCE = 0.010
        
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
        
        self.marker_layer.markers = []
        self.lines_layer.polylines = []

        self.marker_layer.markers.append(
            fm.Marker(
                width=128,
                height=128,
                expand=True,
                coordinates=self.center,
                content=ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.GREY, size=64),
                            ft.Text("You", size=12, weight=ft.FontWeight.BOLD)
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    bgcolor=ft.Colors.TRANSPARENT,
                    border_radius=3
                )
            )
        )


        for peer in services:
            ip = peer.get('ip')
            port = peer.get('port')
            identifier = peer.get('identifier')

            if user.get("identifier", None) == identifier:
                continue
            
            print(f"Identifier peer: {identifier}")

            # Encontra uma posição válida
            lat, lon = find_valid_position(positions)
            positions.append((lat, lon))
            
            # Cria o marker
            self.marker_layer.markers.append(
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

            connected = identifier in [p.get("identifier", None) for p in peers]
            if connected:
                self.lines_layer.polylines.append(
                    fm.PolylineMarker(
                        border_stroke_width=3,
                        border_color=ft.Colors.GREEN,
                        gradient_colors=[
                            ft.Colors.BLACK,
                            ft.Colors.BLACK,
                        ],
                        coordinates=[
                            self.center,
                            fm.MapLatitudeLongitude(lat, lon)
                        ],
                    )
                )
    
        self.marker_layer.update()
        self.lines_layer.update()
        self.page.update()

    def updatePeers(self, peers):
        try:
            # Verifica se está na página sem causar RuntimeError
            if not hasattr(self.marker_layer, 'page') or self.marker_layer.page is None:
                return
        except RuntimeError:
            return
        

        try:
            # Limpa a lista atual
            self.peers_list.controls.clear()
            
            if not peers or len(peers) == 0:
                # Mostra mensagem quando não há peers conectados
                self.peers_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.PERSON_OFF, size=40, color=ft.Colors.GREY_400),
                            ft.Text("Nenhum peer conectado", size=12, color=ft.Colors.GREY_400),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        alignment=ft.alignment.center,
                        padding=20
                    )
                )
            else:
                # Adiciona cada peer à lista
                for peer in peers:
                    # Extrai informações do peer (ajuste conforme a estrutura dos seus dados)
                    peer_id = peer.get("identifier","Unknown")
                    peer_ip = peer.get("ip", "Unknown")
                    peer_port = peer.get("port", "Unknown")
                    peer_name = peer.get("name", peer_id)
                    
                    # Verifica se o peer está online
                    is_online = peer.get("online", True)
                    status_color = ft.Colors.GREEN if is_online else ft.Colors.RED
                    status_text = "Online" if is_online else "Offline"
                    
                    # Cria o card para cada peer
                    peer_card = ft.Container(
                        content=ft.Column([
                            # Header com ícone e nome
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.COMPUTER, 
                                    size=20, 
                                    color=ft.Colors.GREEN_400 if is_online else ft.Colors.GREY_400
                                ),
                                ft.Text(
                                    peer_name, 
                                    size=13, 
                                    weight=ft.FontWeight.BOLD, 
                                    color=ft.Colors.WHITE,
                                    expand=True
                                ),
                                ft.Container(
                                    content=ft.Text(status_text, size=9, color=status_color),
                                    bgcolor=ft.Colors.BLACK26,
                                    border_radius=10,
                                    padding=ft.padding.all(4)
                                )
                            ], spacing=8),
                            
                            # Informações de conexão
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.COMPUTER, size=12, color=ft.Colors.GREY_400),
                                        ft.Text(f"{peer_ip}:{peer_port}", size=10, color=ft.Colors.GREY_400, selectable=True),
                                    ], spacing=4),
                                    
                                    # Identificador (se existir)
                                    ft.Row([
                                        ft.Icon(ft.Icons.COMPUTER, size=12, color=ft.Colors.GREY_400),
                                        ft.Text(peer_id[:20] + "..." if len(peer_id) > 20 else peer_id, 
                                            size=9, color=ft.Colors.GREY_500),
                                    ], spacing=4) if peer_id != "Unknown" else ft.Container(),
                                ], spacing=3),
                                padding=ft.padding.only(left=5, top=5, bottom=5)
                            ),
                            
                            ft.Divider(height=1, color=ft.Colors.GREY_800),
                            
                            # Botões de ação
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.FOLDER_OPEN,
                                    icon_size=18,
                                    tooltip="Ver arquivos",
                                    icon_color=ft.Colors.BLUE,
                                    on_click=lambda e, p=peer: self.show_peer_files(p)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_size=18,
                                    tooltip="Desconectar",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e, ip=peer_ip, port=peer_port: self.disconnect_peer(ip, port)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.INFO,
                                    icon_size=18,
                                    tooltip="Informações",
                                    icon_color=ft.Colors.ORANGE_400,
                                    on_click=lambda e, p=peer: self.show_peer_info(p)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=5)
                        ], spacing=6),
                        bgcolor=ft.Colors.GREY_900,
                        border_radius=10,
                        padding=ft.padding.all(10),
                        margin=ft.margin.only(bottom=5),
                        shadow=ft.BoxShadow(
                            spread_radius=0.5,
                            blur_radius=5,
                            color=ft.Colors.BLACK26
                        )
                    )
                    
                    self.peers_list.controls.append(peer_card)
            
            self.peers_list.update()
            if hasattr(self, 'page') and self.page:
                self.page.update()
        
        except Exception as e:
            # Pegamos o rastro (traceback) que está guardado dentro do 'e'
            tb = e.__traceback__
            
            # Navegamos até o último frame (onde o erro realmente aconteceu)
            while tb.tb_next:
                tb = tb.tb_next
            
            # Agora acessamos o frame e o código
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            logger.info(f" Erro no arquivo: {arquivo}, linha: {linha}")

            logger.info(f"Erro ao executar: {e}")
            

    def show_peer_info(self, peer):
        """Mostra informações detalhadas do peer"""
        peer_id = peer.get("identifier", peer.get("id", "Unknown"))
        peer_ip = peer.get("ip", peer.get("address", "Unknown"))
        peer_port = peer.get("port", "Unknown")
        peer_name = peer.get("name", peer_id)
        
        # Cria dialog com informações
        info_dialog = ft.AlertDialog(
            title=ft.Text(f"Informações do Peer", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.COMPUTER, size=40, color=ft.Colors.BLUE_400),
                        ft.Text(peer_name, size=16, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Divider(),
                    
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DNS, color=ft.Colors.BLUE),
                        title=ft.Text("IP Address", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(peer_ip, selectable=True),
                    ),
                    
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.POWER_INPUT, color=ft.Colors.ORANGE),
                        title=ft.Text("Porta", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(str(peer_port)),
                    ),
                    
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.QR_CODE_SCANNER, color=ft.Colors.PURPLE),
                        title=ft.Text("Identificador", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(peer_id, selectable=True),
                    ),
                    
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.UPDATE, color=ft.Colors.GREEN),
                        title=ft.Text("Status", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text("Online" if peer.get("online", True) else "Offline"),
                    ),
                    
                    ft.Row([
                        ft.TextButton(
                            "Copiar IP",
                            icon=ft.Icons.COPY,
                            on_click=lambda e: self.copy_to_clipboard(peer_ip)
                        ),
                        ft.TextButton(
                            "Copiar ID",
                            icon=ft.Icons.COPY,
                            on_click=lambda e: self.copy_to_clipboard(peer_id)
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
                ], spacing=5),
                width=400,
                padding=10
            ),
            actions=[
                ft.TextButton(
                    "Fechar",
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: self.close_dialog(info_dialog)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=True
        )
        
        self.page.dialog = info_dialog
        self.page.update()

    def copy_to_clipboard(self, text):
        """Copia texto para área de transferência"""
        self.page.set_clipboard(text)
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"✅ Copiado: {text}"),
                duration=2000
            )
        )
