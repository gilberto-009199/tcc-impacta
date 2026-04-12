import asyncio
import sddp_discovery_protocol as sddp

import logging

logger = logging.getLogger(__name__)

class Network:
    def __init__(self, ):
        logger.info("Network instanciado")
    
    def start_server(self, headers, advertise_interval = 60):
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.start_server_async(headers, advertise_interval))
        except KeyboardInterrupt:
            logger.info("Servidor interrompido manualmente.")
        finally:
            loop.close()

    async def search_services_async(self, pattern, wait_time, max_responses = 10):
        """
        Busca serviços na rede (versão assíncrona).
        
        Args:
            pattern (str): Padrão de busca (ex: "calculator:basic").
            wait_time (float): Tempo máximo de espera em segundos.
            max_responses (int): Número máximo de respostas a coletar.
        
        Returns:
            list: Lista de dicionários com informações dos serviços encontrados.
        """
        logger.info("Buscando serviços com padrão '%s'...", pattern)
        results = []
        async with sddp.SddpClient() as client:
            async with client.search(search_pattern=pattern, response_wait_time=wait_time, max_responses=max_responses) as search_req:
                async for response_info in search_req.iter_responses():
                    results.append(response_info)
                    logger.debug("Resposta recebida: %s", response_info)
        logger.info("Busca concluída. %d serviço(s) encontrado(s).", len(results))
        return results