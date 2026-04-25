import logging
logger = logging.getLogger(__name__)

import flet as ft

class SettingsPage(ft.Container):
    def __init__(self, app, uiManager, page):

        logging.info(f"{__name__} iniciou!")

        self.app = app
        self.uiManager = uiManager
        
        appData = self.app.appData
        data = appData.getData()
        network = data.network.value
        user = data.user.value

        toggleOnline = ft.Switch(value=user.get('online'), label="Online", on_change=lambda val: appData.setData(data.user,{ "online": val.data }))
        toggleService = ft.Switch(value=user.get('service'), label="Service Discover", on_change=lambda val: appData.setData(data.user,{ "service": val.data }))
        toggleUPNP = ft.Switch(value=user.get('upnp'), label="UPNP", on_change=lambda val: appData.setData(data.user,{ "upnp": val.data }))
        frmServices = ft.Row([
            toggleOnline,
            toggleService,
            toggleUPNP
        ], alignment=ft.MainAxisAlignment.CENTER)
        

        inputIpLocal = ft.Text(f"+ IP Local: {network.get('ipLocal') or '...'}", size=14)
        inputIpExternal = ft.Text(f"+ IP External: {network.get('ipExternal') or '...'}", size=14)
        frmNetwork = ft.Column([
            inputIpLocal,
            inputIpExternal
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        
        super().__init__(
            content=ft.Column([
                ft.Text("Settings Principal", size=30, weight="bold"),
                
                ft.Divider(height=20),
                frmServices,
                
                ft.Divider(height=20),
                frmNetwork

            ],
            expand=True)
        )


        def reactUser(data):
            toggleOnline.value = data.get('online')
            toggleService.value = data.get('service')
            toggleUPNP.value = data.get('upnp')
            #toggleOnline.update()
            #toggleService.update()
            #toggleUPNP.update()
        data.user.subscribe(on_next=reactUser)

        def reactNetwork(data):
            inputIpLocal.value = f"+ IP Local: {data.get('ipLocal') or '...'}"
            inputIpExternal.value = f"+ IP External: {data.get('ipExternal') or '...'}"
            #inputIpLocal.update()
            #inputIpExternal.update()
        data.network.subscribe(on_next=reactNetwork)