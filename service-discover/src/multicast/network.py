import logging
import asyncio
import sddp_discovery_protocol as sddp

class Network:
    def __init__(self, discover_service=None):
        """
        Inicializa a rede para service discovery com SDDP.
        
        Args:
            discover_service (dict, opcional): Se fornecido, configura o servidor para anunciar o serviço.
                Deve conter as chaves necessárias, como "Type", "Name", etc.
        """
        self.discover_service = discover_service
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        print("Network instanciado")

    async def start_server_async(self, headers: dict = None, advertise_interval: int = 60):
        """
        Inicia o servidor SDDP para anunciar o serviço (versão assíncrona).
        
        Args:
            headers (dict): Cabeçalhos do dispositivo. Se None, usa self.discover_service.
            advertise_interval (int): Intervalo entre anúncios em segundos.
        """
        device_headers = headers or self.discover_service
        if device_headers is None:
            raise ValueError("Nenhum cabeçalho de dispositivo fornecido para o servidor.")

        self.logger.info("Iniciando servidor SDDP com cabeçalhos: %s", device_headers)
        async with sddp.SddpServer(device_headers=device_headers, advertise_interval=advertise_interval) as server:
            self.logger.info("Servidor SDDP rodando. Pressione Ctrl+C para parar.")
            await server.wait_for_done()  # Aguarda até ser interrompido

    def start_server(self, headers: dict = None, advertise_interval: int = 60):
        """
        Inicia o servidor SDDP (versão síncrona, bloqueante).
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.start_server_async(headers, advertise_interval))
        except KeyboardInterrupt:
            self.logger.info("Servidor interrompido manualmente.")
        finally:
            loop.close()

    async def search_services_async(self, pattern: str = "*", wait_time: float = 3.0, max_responses: int = 10):
        """
        Busca serviços na rede (versão assíncrona).
        
        Args:
            pattern (str): Padrão de busca (ex: "calculator:basic").
            wait_time (float): Tempo máximo de espera em segundos.
            max_responses (int): Número máximo de respostas a coletar.
        
        Returns:
            list: Lista de dicionários com informações dos serviços encontrados.
        """
        self.logger.info("Buscando serviços com padrão '%s'...", pattern)
        results = []
        async with sddp.SddpClient() as client:
            async with client.search(search_pattern=pattern, response_wait_time=wait_time, max_responses=max_responses) as search_req:
                async for response_info in search_req.iter_responses():
                    results.append(response_info)
                    self.logger.debug("Resposta recebida: %s", response_info)
        self.logger.info("Busca concluída. %d serviço(s) encontrado(s).", len(results))
        return results

    def search_services(self, pattern: str = "*", wait_time: float = 3.0, max_responses: int = 10):
        """
        Busca serviços na rede (versão síncrona).
        
        Returns:
            list: Lista de serviços encontrados.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.search_services_async(pattern, wait_time, max_responses))
        finally:
            loop.close()