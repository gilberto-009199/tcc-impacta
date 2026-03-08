import asyncio
from src.multicast.network import Network

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

class DiscoverService:

    def __init__(self, app):
        self.app = app

        self.server = asyncio.ALL_COMPLETED
        self.network = Network(self)

        self.queuePeers = []

    def config(
        self,
        headers = headers_default
    ):
        
        self.server = asyncio.create_task(
            self.network.start_server_async(headers = headers)
        )

    async def serve(self):
        await self.server

    async def find(
        self,
        headers = headers_default,
        wait_time = wait_time_default
    ):
        services = await self.network.search_services_async(
            pattern=headers["Type"], 
            wait_time = wait_time
        );

        return services;
        
