import base64
import logging
import asyncio

logger = logging.getLogger(__name__)

from app.util.IPUtil import IPUtil
from app.ssdp.multicast.network import Network



wait_time_default = 5 # 5s
headers_default = {
    "Type": "Acme:TestDevice",
    "Primary-Proxy": "test-device",
    "Proxies": "test-device",
    "Manufacturer": "Acme",
    "Model": "TestDevPlus",
    "Port": 97777,
    "Identifier": "==9hu43r39h4r93h4534h5oiuh",
    "Driver": "test-device_Acme_TestDevPlus.c4i",
};

class SSDPManager():    
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app
        self.network = Network()
        
        data = app.appData.getData()
        data.user.subscribe(on_next=lambda val: self.config())
        data.network.subscribe(on_next=lambda val: self.config())

    def config(self):
        logging.info(f"{__name__} config iniciado!")

        data = self.app.appData.getData()
        user = data.user.value
        
        if not user.get("online"):
            self.stop()
            return;

        if not user.get("service"):
            self.stop()
            return;

        headers_default["Port"] = data.network.value.get("port", headers_default["Port"])
        headers_default["Identifier"] = base64.b64encode(data.user.value.get("identifier", headers_default["Identifier"])).decode('utf-8')

        self.run()

    def run(self, headers= headers_default):
        """Inicia o servidor SSDP (síncrono em thread)"""
        logger.info("Iniciando SSDP Manager...")
        
        try:
            # Iniciar servidor (síncrono, roda em thread separada)
            self.network.start_server(headers, advertise_interval=60)
            logger.info("Servidor SSDP iniciado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor SSDP: {e}")
    
    def stop(self):
        """Para o servidor SSDP (síncrono)"""
        logger.info("Parando SSDP Manager...")
        try:
            self.network.stop_server()
            logger.info("Servidor SSDP parado")
        except Exception as e:
            logger.error(f"Erro ao parar servidor SSDP: {e}")

    async def findPeers(self, headers= headers_default):
        """
        Busca serviços na rede (síncrono)
        """
        data = self.app.appData.getData()
        networkData = data.network.value
        ipList = networkData.get("ips")

        try:
          
            services = self.network.search_services_sync(headers["Type"], wait_time_default, 10)
            
            logger.info(f"Encontrados {len(services)} serviços")

            servicesFilter = []

            for svc in services:
                src_addr = getattr(svc, 'src_addr', False)
                datagram = getattr(svc, 'datagram', False)
                ip, port = src_addr
                port = datagram.headers.get('Port', '')
                identifier = datagram.headers.get('Identifier', '')
                data = (
                    ip,
                    port,
                    identifier
                )

                if src_addr:
                    #if ip not in ipList:
                    servicesFilter.append(data)

            return servicesFilter
        except Exception as e:
            logger.error(f"Erro na busca de serviços: {e}")
            return []

        

