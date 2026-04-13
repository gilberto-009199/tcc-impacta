import asyncio
import sddp_discovery_protocol as sddp
import threading
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Network:
    def __init__(self):
        logger.info("Network instanciado")
        self.server_thread: Optional[threading.Thread] = None
        self.server_running = False
        self.server_loop: Optional[asyncio.AbstractEventLoop] = None
    
    def start_server(self, headers, advertise_interval=60):
        """
        Inicia o servidor em uma thread separada (síncrono).
        """
        if self.server_running:
            logger.warning("Servidor já está rodando")
            return
        
        logger.info("Iniciando servidor em thread separada...")
        self.server_running = True
        
        # Criar e iniciar thread para o servidor
        self.server_thread = threading.Thread(
            target=self._run_server_in_thread,
            args=(headers, advertise_interval),
            daemon=True
        )
        self.server_thread.start()
        
        # Aguardar um pouco para o servidor iniciar
        time.sleep(1)
        logger.info("Servidor iniciado na thread: %s", self.server_thread.name)
    
    def _run_server_in_thread(self, headers, advertise_interval):
        """
        Executa o servidor em uma thread separada com seu próprio event loop.
        """
        # Criar novo event loop para esta thread
        self.server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.server_loop)
        
        try:
            logger.info("Servidor iniciado!!!!")
            self.server_loop.run_until_complete(
                self.start_server_async(headers, advertise_interval)
            )
            logger.info("Star ASYNC RUN!!!!")
        except KeyboardInterrupt:
            logger.info("Servidor interrompido manualmente.")
        except Exception as e:
            logger.error(f"Erro no servidor: {e}")
        finally:
            self.server_running = False
            self.server_loop.close()
            logger.info("Servidor finalizado")
    
    def stop_server(self):
        """
        Para o servidor (síncrono).
        """
        if not self.server_running:
            logger.warning("Servidor não está rodando")
            return
        
        logger.info("Parando servidor...")
        
        if self.server_loop:
            # Parar o event loop da thread
            self.server_loop.call_soon_threadsafe(self.server_loop.stop)
        
        if self.server_thread and self.server_thread.is_alive():
            # Aguardar a thread terminar (timeout de 5 segundos)
            self.server_thread.join(timeout=5)
            
            if self.server_thread.is_alive():
                logger.warning("Thread do servidor não terminou dentro do timeout")
        
        self.server_running = False
        logger.info("Servidor parado")
    
    async def start_server_async(self, headers, advertise_interval=60):
        """
        Inicia o servidor SDDP (versão assíncrona).
        Implemente aqui a lógica real do servidor
        """
        logger.info("Servidor async iniciado com headers: %s", headers)
        
        try:
            # Exemplo de servidor SDDP
            # async with sddp.SddpServer() as server:
            #     await server.advertise(headers, advertise_interval)
            #     # Manter servidor rodando
            #     while self.server_running:
            #         await asyncio.sleep(1)
            
            # Simulação de servidor rodando
            while self.server_running:
                await asyncio.sleep(1)
                async with sddp.SddpServer(device_headers=headers, advertise_interval=advertise_interval) as server:
                    logger.info("Servidor SDDP rodando. Pressione Ctrl+C para parar.")
                    await server.wait_for_done()  
                logger.debug("Servidor ativo...")
                
        except asyncio.CancelledError:
            logger.info("Servidor async cancelado")
        except Exception as e:
            logger.error(f"Erro no servidor async: {e}")
            raise
    
    def search_services(self, pattern, wait_time=8, max_responses=10) -> List[Dict[str, Any]]:
        """
        Busca serviços na rede (versão síncrona usando thread).
        
        Args:
            pattern (str): Padrão de busca (ex: "calculator:basic").
            wait_time (float): Tempo máximo de espera em segundos.
            max_responses (int): Número máximo de respostas a coletar.
        
        Returns:
            list: Lista de dicionários com informações dos serviços encontrados.
        """
        logger.info("Buscando serviços com padrão '%s'...", pattern)
        
        # Usar ThreadPoolExecutor para rodar a busca async em thread separada
        import concurrent.futures
        
        def run_async_search():
            # Criar novo event loop para esta thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.search_services_async(pattern, wait_time, max_responses)
                )
            finally:
                loop.close()
        
        # Executar em thread separada
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_async_search)
            try:
                results = future.result(timeout=wait_time + 5)
                logger.info("Busca concluída. %d serviço(s) encontrado(s).", len(results))
                return results
            except concurrent.futures.TimeoutError:
                logger.error("Timeout na busca de serviços")
                return []
            except Exception as e:
                logger.error(f"Erro na busca de serviços: {e}")
                return []
    
    async def search_services_async(self, pattern, wait_time=6, max_responses=10) -> List[Dict[str, Any]]:
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
        
        try:
            async with sddp.SddpClient() as client:
                async with client.search(
                    search_pattern=pattern, 
                    response_wait_time=wait_time, 
                    max_responses=max_responses
                ) as search_req:
                    async for response_info in search_req.iter_responses():
                        results.append(response_info)
                        logger.debug("Resposta recebida: %s", response_info)
        except asyncio.CancelledError:
            logger.warning("Busca cancelada")
        except Exception as e:
            logger.error(f"Erro durante busca async: {e}")
        
        logger.info("Busca concluída. %d serviço(s) encontrado(s).", len(results))
        return results
    
    def is_server_running(self) -> bool:
        """Verifica se o servidor está rodando"""
        return self.server_running
    
    def get_server_thread_id(self) -> Optional[int]:
        """Retorna o ID da thread do servidor"""
        if self.server_thread and self.server_thread.is_alive():
            return self.server_thread.ident
        return None