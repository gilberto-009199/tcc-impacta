import asyncio
from src.multicast.network import Network

class DiscoverService:

    def __init__(self, app):
        print("DiscoverService intanciado")
        self.app = app
        self.queuePeers = []
        self.network = Network(self)

    async def run(self):
        """Executa servidor e cliente (versão assíncrona)"""
        # Inicia o servidor em uma tarefa separada
        server_task = asyncio.create_task(
            self.network.start_server_async(headers={
                "Type": "Acme:TestDevice",
                "Primary-Proxy": "test-device",
                "Proxies": "test-device",
                "Manufacturer": "Acme",
                "Model": "TestDevPlus",
                "Satus"
                "Driver": "test-device_Acme_TestDevPlus.c4i",
            })
        )
        
        # Dá um tempo para o servidor iniciar
        await asyncio.sleep(2)
        
        # Faz a busca
        services = await self.network.search_services_async(
            pattern="Acme:TestDevice", 
            wait_time=5
        )
        
        for svc in services:
            print(f"Serviço encontrado em {svc['src_addr']}")
            print(f"Cabeçalhos: {svc['headers']}")
        
        # Aguarda o servidor (opcional - fica rodando)
        await server_task
