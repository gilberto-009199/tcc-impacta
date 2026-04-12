import socket

import urllib.request
import logging

logger = logging.getLogger(__name__)

class IPUtil:
    @staticmethod
    def getLocalIP():
        """Obtém o IP local da máquina"""
        try:
            # Cria um socket UDP para determinar a interface de rede ativa
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.error(f"Erro ao obter IP local: {e}")
            return "127.0.0.1"
    
    @staticmethod
    def getExternalIP():
        """Obtém o IP externo da máquina usando um serviço web"""
        urls = [
            "https://api.ipify.org", 
            "https://ident.me", 
            "https://icanhazip.com"
        ]
        
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    return response.read().decode('utf-8').strip()
            except Exception as e:
                logger.warning(f"Falha ao acessar {url}: {e}")
                continue
        
        return False

if __name__ == "__main__":
    
    ipLocal = IPUtil.getLocalIP()
    ipExternal = IPUtil.getExternalIP()

    print(f"""
        Local: {ipLocal}
        External: {ipExternal}
    """)

