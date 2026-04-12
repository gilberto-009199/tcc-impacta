import logging

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
    "Satus"
    "Driver": "test-device_Acme_TestDevPlus.c4i",
};

class SSDPManager():    
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app
        self.network = Network(self)
        
        data = app.appData.getData()
        data.user.subscribe(on_next=lambda val: self.config())

    async def config(self):
        logging.info(f"{__name__} config iniciado!")

        data = self.app.appData.getData()
        user = data.user.value

        if not user.get("online"):
            return;

        ipLocal = IPUtil.getLocalIP()
        ipExternal = IPUtil.getExternalIP()
        
        self.app.appData.setData(data.network,
            {
                "ipLocal": ipLocal,
                "ipExternal": ipExternal
            }
        )

        if not user.get("service"):
            return;

        await self.run()

    def run(self,
            headers = headers_default
    ):
        logging.info(f"{__name__} run iniciado!")
        
        try:
            self.network.start_server(headers)
            logger.info("Servidor SSDP iniciado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor SSDP: {e}")
        

    async def find(
        self,
        headers = headers_default,
        wait_time = wait_time_default
    ):
        services = await self.network.search_services_async(
            pattern=headers["Type"], 
            wait_time = wait_time,
            max_responses = 100
        );

        return services;

        

