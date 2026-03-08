import asyncio
from src.multicast.discoverService import DiscoverService

class App:
    
    def __init__(self):
        print("App intanciado")
        self.discoverService = DiscoverService(self);


    async def run(self):
        
        print("App iniciando")
        
        self.discoverService.config();
        
        print("App inicializado!!!!")
        
        self.discoverService.serve();
        
        await asyncio.sleep(2)
        
        services = await self.discoverService.find();
        
        for svc in services:

            src_addr = getattr(svc, 'src_addr', 'none')
            headers = getattr(svc, 'src_addr', 'none')

            print(f"Serviço encontrado em {src_addr}")
            print(f"Cabeçalhos: {headers}")

        print("App finalizado")

app = App()