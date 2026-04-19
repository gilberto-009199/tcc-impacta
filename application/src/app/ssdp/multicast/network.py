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
            async with sddp.SddpServer(device_headers=headers, advertise_interval=advertise_interval) as server:
                logger.info("Servidor SDDP rodando. Pressione Ctrl+C para parar.")
                # Manter servidor rodando
                while self.server_running:
                    await asyncio.sleep(1)
                    logger.debug("Servidor ativo...")
                
        except asyncio.CancelledError:
            logger.info("Servidor async cancelado")
        except Exception as e:
            logger.error(f"Erro no servidor async: {e}")
            raise
    
    def search_services_sync(self, pattern, wait_time=6, max_responses=10) -> List[Dict[str, Any]]:
        """
        Busca serviços na rede (versão síncrona).
        """
        if wait_time <= 0 or max_responses <= 0:
            raise ValueError("wait_time e max_responses devem ser positivos")
        
        logger.info("Buscando serviços com padrão '%s' (timeout=%ds, max=%d)", 
                    pattern, wait_time, max_responses)
        results = []
        start_time = time.time()
        
        client = None
        search_req = None
        
        try:
            # Cria cliente (sem context manager)
            client = sddp.SddpClient()
            
            # Inicia busca (sem context manager)
            search_req = client.search(
                search_pattern=pattern, 
                response_wait_time=min(wait_time, 30),
                max_responses=max_responses
            )
            
            # Itera respostas
            for response_info in search_req.iter_responses():
                results.append(response_info)
                logger.debug("Resposta recebida: %s", response_info)
                
                if len(results) >= max_responses:
                    logger.debug("Máximo de respostas atingido")
                    continue
                
                if time.time() - start_time >= wait_time:
                    logger.debug("Timeout total atingido")
                    continue
                                
        except Exception as e:
            logger.error("Erro durante busca para padrão '%s': %s", pattern, e, exc_info=True)
        finally:
            # Limpeza manual
            if search_req:
                try:
                    search_req.close()  # Tenta fechar a requisição
                except Exception as e:
                    logger.debug("Erro ao fechar search_req: %s", e)
            
            if client:
                try:
                    client.close()  # Tenta fechar o cliente
                except Exception as e:
                    logger.debug("Erro ao fechar client: %s", e)
        
        logger.info("Busca concluída. %d serviço(s) encontrado(s) para '%s'", 
                    len(results), pattern)
        return results


    
    def is_server_running(self) -> bool:
        """Verifica se o servidor está rodando"""
        return self.server_running
    
    def get_server_thread_id(self) -> Optional[int]:
        """Retorna o ID da thread do servidor"""
        if self.server_thread and self.server_thread.is_alive():
            return self.server_thread.ident
        return None