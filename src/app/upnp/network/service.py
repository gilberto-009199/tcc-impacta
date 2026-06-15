import flet as ft

import socket
import upnpy
from upnpy.exceptions import SOAPError

from .network import Network

import logging

logger = logging.getLogger(__name__)

class UPNPService:
    
    def __init__(self, app):
        """
        Inicializa o serviço UPnP com uma instância de Network
        
        Args:
            network: Instância da classe Network
        """
        self.network = Network()
        self.upnp = None
        self.router = None
        self.dispositivo_conectado = False
        logger.info("UPNPService initialized")
    
    def config(self):
        """Configura e descobre dispositivos UPnP na rede"""
        try:
            
            socket.setdefaulttimeout(1.8)
            self.upnp = upnpy.UPnP()
                        
            logger.info("🔍 Procurando dispositivos UPnP...")
            
            devices = self.upnp.discover()

            logger.info(f"  Encontrados {devices} dispositivos")
            
            if len(devices) == 0:
                logger.warning("❌ Nenhum dispositivo UPnP encontrado!")
                return False
            
            # Selecionar o gateway (roteador)
            socket.setdefaulttimeout(1.8)
            self.router = self.upnp.get_igd()
            self.router.get_services()
            
            # Obter IP externo e atualizar o Network
            ip_externo = self._get_external_ip()
            self.network.set_external_ip(ip_externo)
            
            logger.info(f"✅ UPnP configurado com sucesso!")
            logger.info(f"  IP Local: {self.network.get_local_ip()}")
            logger.info(f"  IP Externo: {self.network.get_external_ip()}")
            
            self.dispositivo_conectado = True

            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na configuração UPnP: {e}")
            return False

    def _get_external_ip(self):
        """Obtém o IP externo do roteador"""
        try:
            
            options = ['WANPPPConnection.1', 'WANIPConn1']
            service = None
            for opt in options:
                if opt in self.router.services:
                    service = self.router[opt]

            ip_externo = service.GetExternalIPAddress()['NewExternalIPAddress']
            self.network.set_external_ip(ip_externo)

            return ip_externo
        
        except Exception as e:
            logger.error(f"❌ Erro ao obter IP externo: {e}")
            return None
        
    def openPort(self, port=9292, protocolo='TCP', descricao="Porta aberta via Python"):
        """Abre uma porta no roteador via UPnP"""
        logger.info(f"openPort ")
        if not self.dispositivo_conectado:
            logger.warning("⚠️  UPnP não configurado. Executando config()...")
            if not self.config():
                return False
        
        self.closePort(port, protocolo)
     
        service = self.getServicesRouter()
        
        logger.info(f"openPort {service}")

        service.AddPortMapping(
            NewRemoteHost='',
            NewExternalPort=port,
            NewProtocol=protocolo,
            NewInternalPort=port,
            NewInternalClient=self.network.get_local_ip(),
            NewEnabled=1,
            NewPortMappingDescription=descricao,
            NewLeaseDuration=0
        )
        
        logger.info("Mapeamento novo com sucesso.")
        
        
        return True

    
    def closePort(self, port=9292, protocolo='TCP'):
        """Fecha uma porta no roteador"""
        
        if not self.dispositivo_conectado:
            logger.warning(" UPnP não configurado. Executando config()...")
            if not self.config():
                return False
        
        service = self.getServicesRouter()

        try:
            
            service.DeletePortMapping(
                NewRemoteHost='',
                NewExternalPort=port,
                NewProtocol=protocolo
            )

            print("Mapeamento antigo removido com sucesso.")
        
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao fechar porta: {e}")
            return False

    def getServicesRouter(self):
        """Retorna os serviços disponíveis no roteador"""
        if self.router:
            options = ['WANPPPConnection.1', 'WANIPConn1']
            service = None
            for opt in options:
                if opt in self.router.services:
                    service = self.router[opt]
            return service
        else:
            logger.warning("⚠️  Roteador não configurado.")
            return None