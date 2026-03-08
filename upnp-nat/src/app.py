import asyncio
from src.upnp.service import UPNPService

class App:
    
    def __init__(self):
        print("App intanciado")
        self.upnpService = UPNPService(self);


    def run(self):
        
        print("App iniciando")
        
        self.upnpService.config();
        
        print("App inicializado!!!!")
        
        self.upnpService.getStatus();
        
        self.upnpService.openPort(9090);
        
        
        print("App finalizado")

app = App()