import socket
import urllib.request
import logging
import netifaces

logger = logging.getLogger(__name__)

class IPUtil:
    @staticmethod
    def getAllLocalIPs():
        """Obtém todos os IPs locais da máquina (incluindo IPv4 e IPv6)"""
        ips = []
        try:
            # Obtém todas as interfaces de rede
            interfaces = netifaces.interfaces()
            
            for interface in interfaces:
                # Obtém os endereços de cada interface
                addrs = netifaces.ifaddresses(interface)
                
                # IPv4
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get('addr')
                        # Filtra localhost e IPs inválidos
                        if ip and not ip.startswith('127.'):
                            ips.append(ip)
                
                # IPv6
                if netifaces.AF_INET6 in addrs:
                    for addr in addrs[netifaces.AF_INET6]:
                        ip = addr.get('addr')
                        # Remove o sufixo de escopo do IPv6 se existir
                        if ip and '%' in ip:
                            ip = ip.split('%')[0]
                        # Filtra localhost IPv6
                        if ip and not ip == '::1':
                            ips.append(ip)
            
            return ips
            
        except Exception as e:
            logger.error(f"Erro ao obter todos os IPs locais: {e}")
            return ips
    
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
    
    @staticmethod
    def getIPv4Addresses():
        """Retorna apenas os endereços IPv4"""
        all_ips = IPUtil.getAllLocalIPs()
        return [ip_info['ip'] for ip_info in all_ips['ipv4']]
    
    @staticmethod
    def getIPv6Addresses():
        """Retorna apenas os endereços IPv6"""
        all_ips = IPUtil.getAllLocalIPs()
        return [ip_info['ip'] for ip_info in all_ips['ipv6']]
    
    @staticmethod
    def printAllIPs():
        """Imprime todos os IPs de forma organizada"""
        all_ips = IPUtil.getAllLocalIPs()
        
        print("\n=== TODOS OS IPS LOCAIS ===")
        
        if all_ips['ipv4']:
            print("\n📡 IPv4 Addresses:")
            for ip_info in all_ips['ipv4']:
                print(f"  • Interface: {ip_info['interface']}")
                print(f"    IP: {ip_info['ip']}")
                print(f"    Máscara: {ip_info['netmask']}")
        else:
            print("\n📡 Nenhum IPv4 encontrado")
        
        if all_ips['ipv6']:
            print("\n🌐 IPv6 Addresses:")
            for ip_info in all_ips['ipv6']:
                print(f"  • Interface: {ip_info['interface']}")
                print(f"    IP: {ip_info['ip']}")
                print(f"    Máscara: {ip_info['netmask']}")
        else:
            print("\n🌐 Nenhum IPv6 encontrado")

if __name__ == "__main__":
    # Configuração básica de logging
    logging.basicConfig(level=logging.INFO)
    
    # Teste das novas funcionalidades
    ipLocal = IPUtil.getLocalIP()
    ipExternal = IPUtil.getExternalIP()
    
    print(f"""
    📍 IP Principal: {ipLocal}
    🌍 IP Externo: {ipExternal}
    """)
    
    # Lista todos os IPs
    IPUtil.printAllIPs()
    
    # Exemplo de como obter apenas as listas de IPs
    print("\n=== EXEMPLOS DE USO ===")
    print(f"Todos IPv4: {IPUtil.getIPv4Addresses()}")
    print(f"Todos IPv6: {IPUtil.getIPv6Addresses()}")