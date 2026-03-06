
from src.multicast.discoverService import DiscoverService

class App:
    
    def __init__(self):
        print("App intanciado")
        self.discoverService = DiscoverService(self);


    async def run(self):
        print("App iniciando")
        print("App inicializado!!!!")
        print("App finalizado")

        await self.discoverService.run();
        


app = App()