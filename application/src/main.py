import os
import logging

logger = logging.getLogger(__name__)

basedir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(basedir, "debug_tcc.log")

logging.basicConfig(
    level=logging.INFO,
    filename=log_path,  # Caminho completo
    filemode='a',       # 'a' para anexar, 'w' para sobrescrever cada vez que abrir
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

import flet as ft
import asyncio


from tcp.src.peersManager import PeerManager

from discover.src.multicast.discoverService import DiscoverService
#from upnp.src.upnp.service import UPNPService

ft.context.disable_auto_update()

def main(page: ft.Page):

    logging.info("O aplicativo iniciou com sucesso!")

    page.title = "P2P App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    status = ft.Text("Pronto", size=16)
    feedback = ft.ListView(
        expand=True, 
        spacing=2, 
        auto_scroll=True,
        height=300,
        divider_thickness=1
    )
    #upnpService = UPNPService(page, feedback)
    discoverService = DiscoverService(page, feedback)
    
    print(f"{__name__} Antes de criar PeerManager")
    peerManager = PeerManager(app=page, feedback=feedback)
    print(f"{__name__} Depois de criar PeerManager")

    def upnp(e):
        status.value = "UPNP"
        # Chame sua função aqui
        feedback.controls.append(ft.Text(f"Botão UPNP clicado", color=ft.Colors.BLACK))
        logging.info("Botão UPNP clicado")

        upnprun(feedback)

        page.update()
    
    async def discover(e):
        status.value = "Service Discover"
        
        discoverService.config();
        logging.info("Service Discover")
        
        feedback.controls.append(ft.Text(f"Service Discover:", color=ft.Colors.BLACK))        
        page.update()

        discoverService.serve();
        
        await asyncio.sleep(2)
        
        services = await discoverService.find();
        
        for svc in services:
            src_addr = getattr(svc, 'src_addr', 'none')
            headers = getattr(svc, 'src_addr', 'none')

            feedback.controls.append(ft.Text(f"Serviço encontrado em {src_addr}", color=ft.Colors.BLACK))
            feedback.controls.append(ft.Text(f"Cabeçalhos: {headers}", color=ft.Colors.BLACK))

        page.update()
    
    def socket(e):
        status.value = "Socket"
        
        feedback.controls.append(ft.Text(f"Socket:", color=ft.Colors.BLACK))
        logger.info("Socket")

        peerManager.run(page)

        page.update()
    
    page.add(
        ft.Column([
            ft.Row(
                [
                    ft.Button("UPNP", on_click=upnp),
                    ft.Button("Service Discover", on_click=discover),
                    ft.Button("Socket", on_click=socket),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=10),
            ft.Row([status], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            ft.Text("Logs do Sistema:", weight="bold"),
            feedback
        ], expand=True)
    )

    page.update()


def upnprun(feedback):
    try:
        import socket
        import upnpy
        from upnpy.exceptions import SOAPError
        socket.setdefaulttimeout(1.8)
        upnp = upnpy.UPnP()

        devices = upnp.discover()

        device = upnp.get_igd()
        device.get_services()


        options = ['WANPPPConnection.1', 'WANIPConn1']
        service = None
        for opt in options:
            if opt in device.services:
                service = device[opt]
                
        service.AddPortMapping.get_input_arguments()
        

        try:

            service.DeletePortMapping(
                NewRemoteHost='',
                NewExternalPort=8080,
                NewProtocol='TCP'
            )
            print("Mapeamento antigo removido com sucesso.")
            feedback.controls.append(
                ft.Text(f"""
                    Mapeamento antigo removido com sucesso.
                """,
                color=ft.Colors.BLACK))
        except Exception as e:
            if '718' in str(e):
                print("Conflito detectado: A porta já está mapeada ou em uso.")
            else:
                raise e

        service.AddPortMapping(
            NewRemoteHost='',
            NewExternalPort=8080,
            NewProtocol='TCP',
            NewInternalPort=8080,
            NewInternalClient='192.168.0.116',
            NewEnabled=1,
            NewPortMappingDescription='Meu Servidor',
            NewLeaseDuration=0
        )
        print("Mapeamento novo com sucesso.")
        feedback.controls.append(
            ft.Text(f"""
                Mapeamento novo com sucesso.
            """,
            color=ft.Colors.BLACK))
    except Exception as e:
        if '718' in str(e):
            print("Conflito detectado: A porta já está mapeada ou em uso.")
        else:
            raise e
ft.run(main)
