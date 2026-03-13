
import time
from src.protocol.client import Client
from src.protocol.server import Server

class App:
    
    def __init__(self):
        print("App intanciado")
        self.server = Server(self);
        self.client = Client(self);


    def run(self):
        print("App iniciando")
        print("App inicializado!!!!")
        print("App finalizado")

        self.server.run();

        time.sleep(10);

        self.client.run();
        

        time.sleep(10);


app = App()