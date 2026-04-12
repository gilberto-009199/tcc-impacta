import flet as ft
import flet_map as fm

class PeerPage(ft.Container):
    def __init__(self, app, uiManager, page):
        self.app = app
        self.uiManager = uiManager

        # Criando pontos
        ponto_a = fm.MapLatitudeLongitude(-23.5505, -46.6333)
        ponto_b = fm.MapLatitudeLongitude(-23.5580, -46.6610)

        # Criando as camadas separadamente
        polygon_layer = fm.PolygonLayer(
            polygons=[
                fm.PolygonMarker(
                    coordinates=[ponto_a, ponto_b],
                    color=ft.Colors.BLUE,
                    border_stroke_width=3
                )
            ]
        )
        
        marker_layer = fm.MarkerLayer(
            markers=[
                fm.Marker(
                    coordinates=ponto_a,
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.GREEN, size=35),
                            ft.Column([
                                ft.Text("ponto A")
                            ])
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ),
                fm.Marker(
                    coordinates=ponto_b,
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.GREEN, size=35),
                            ft.Column([
                                ft.Text("ponto B"),
                                ft.Text("ponto B"),
                                ft.Text("ponto B"),
                                ft.Text("ponto B"),
                                ft.Text("ponto B"),
                            ])
                        ],
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
            ]
        )
        appData = self.app.appData
        data = appData.getData()
        user = data.user.value

        toggleOnline = ft.Switch(value=user.get('service'), label="Service Discover", on_change=lambda val: appData.setData(data.user,{ "service": val.data }))
        btnServiceDiscover = ft.Button("Find Peers", on_click=self.findPeers)

        super().__init__(
            content=ft.Column([
                    ft.Row([
                            ft.Divider(),
                            ft.Container(expand=True),
                            btnServiceDiscover,
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
                    fm.Map(
                        expand=True,
                        initial_center=ponto_a,
                        layers=[
                            polygon_layer,
                            marker_layer
                        ]
                    )
                ],
                expand=True
            )
        )

    async def findPeers(self):
        services = await self.app.ssdp.find()
        print(f"{services}")