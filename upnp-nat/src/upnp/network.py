import miniupnpc
import socket


class Network:
    def __init__(self):
        self.ip_local = self._get_local_ip()
        self.ip_externo = None
        print(f"📡 Network initialized")
        print(f"  IP Local: {self.ip_local}")
    
    def _get_local_ip(self):
        """Obtém o IP local da máquina"""
        try:
            # Cria uma conexão fake para descobrir o IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def set_external_ip(self, ip):
        """Define o IP externo (vindo do UPnP)"""
        self.ip_externo = ip
        print(f"  IP Externo: {self.ip_externo}")
    
    def get_local_ip(self):
        """Retorna o IP local"""
        return self.ip_local
    
    def get_external_ip(self):
        """Retorna o IP externo"""
        return self.ip_externo