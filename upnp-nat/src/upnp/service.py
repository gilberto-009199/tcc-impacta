from upnpy import UPnP

from src.upnp.network import Network

class UPNPService:
    
    def __init__(self, app):
        """
        Inicializa o serviço UPnP com uma instância de Network
        
        Args:
            network: Instância da classe Network
        """
        self.network = Network()
        self.upnp = UPnP()
        self.device = None
        self.dispositivo_conectado = False
        print("🔌 UPNPService initialized")
    
    def config(self):
        """Configura e descobre dispositivos UPnP na rede"""
        try:
            # Descobrir dispositivos
            print("🔍 Procurando dispositivos UPnP...")
            devices = self.upnp.discover()
            
            num_devices = len(devices)
            print(f"  Encontrados {num_devices} dispositivos")
            
            if num_devices == 0:
                print("❌ Nenhum dispositivo UPnP encontrado!")
                return False
            
            # Procurar por um dispositivo de gateway (IGD)
            for device in devices:
                if 'InternetGatewayDevice' in device.device_type:
                    self.device = device
                    break
            
            # Se não encontrou IGD específico, usar o primeiro dispositivo
            if self.device is None:
                self.device = devices[0]
            
            # Obter IP externo
            try:
                ip_externo = self._get_external_ip()
                if ip_externo:
                    self.network.set_external_ip(ip_externo)
            except:
                print("⚠️  Não foi possível obter IP externo")
            
            print(f"✅ UPnP configurado com sucesso!")
            print(f"  IP Local: {self.network.get_local_ip()}")
            print(f"  IP Externo: {self.network.get_external_ip()}")
            
            self.dispositivo_conectado = True
            return True
            
        except Exception as e:
            print(f"❌ Erro na configuração UPnP: {e}")
            return False
    
    def _get_external_ip(self):
        """Obtém o IP externo via WANIPConnection ou WANPPPConnection"""
        try:
            # Procurar pelos serviços de PppConnection/IpConnection
            for device in self.upnp.discover():
                services = device.get_services()
                for service in services:
                    if 'WANIPConnection' in service.service_type or 'WANPPPConnection' in service.service_type:
                        # Tentar obter IP externo
                        try:
                            result = service.GetExternalIPAddress()
                            if result and 'NewExternalIPAddress' in result:
                                return result['NewExternalIPAddress']
                        except:
                            pass
            return None
        except:
            return None
    
    def _porta_ja_existe(self, port, protocolo):
        """Verifica se uma porta já está mapeada"""
        try:
            if not self.device:
                return False, None
            
            # Procurar pelo serviço de WANIPConnection ou WANPPPConnection
            services = self.device.get_services()
            for service in services:
                if 'WANIPConnection' in service.service_type or 'WANPPPConnection' in service.service_type:
                    try:
                        # Listar todas as portas
                        index = 0
                        while True:
                            try:
                                result = service.GetGenericPortMappingEntry(NewPortMappingIndex=index)
                                if not result:
                                    break
                                
                                external_port = result.get('NewExternalPort')
                                protocol = result.get('NewProtocol', 'TCP')
                                
                                if external_port == str(port) and protocol.upper() == protocolo.upper():
                                    return True, result
                                
                                index += 1
                            except:
                                break
                    except:
                        pass
            
            return False, None
            
        except Exception as e:
            print(f"Erro ao verificar portas existentes: {e}")
            return False, None
    
    def openPort(self, port=9292, protocolo='TCP', descricao="Porta aberta via Python"):
        """Abre uma porta no roteador via UPnP"""
        
        if not self.dispositivo_conectado:
            print("⚠️  UPnP não configurado. Executando config()...")
            if not self.config():
                return False
        
        try:
            # Verificar se a porta já existe
            existe, mapping = self._porta_ja_existe(port, protocolo)
            
            if existe:
                print(f"ℹ️  Porta {port}/{protocolo} já está aberta!")
                print(f"  {mapping.get('NewInternalClient')}:{mapping.get('NewInternalPort')} → {mapping.get('NewExternalPort')}/{mapping.get('NewProtocol')}")
                return True
            
            # Adicionar mapeamento
            ip_local = self.network.get_local_ip()
            
            if not self.device:
                print("❌ Dispositivo não configurado")
                return False
            
            # Procurar pelo serviço de WANIPConnection ou WANPPPConnection
            services = self.device.get_services()
            for service in services:
                if 'WANIPConnection' in service.service_type or 'WANPPPConnection' in service.service_type:
                    try:
                        resultado = service.AddPortMapping(
                            NewRemoteHost='',
                            NewExternalPort=str(port),
                            NewProtocol=protocolo.upper(),
                            NewInternalPort=str(port),
                            NewInternalClient=ip_local,
                            NewEnabled='1',
                            NewPortMappingDescription=descricao,
                            NewLeaseDuration='0'
                        )
                        
                        print(f"✅ Porta {port}/{protocolo} aberta com sucesso!")
                        print(f"  {self.network.get_external_ip()}:{port} → {ip_local}:{port}")
                        return True
                    except Exception as e:
                        print(f"❌ Erro ao adicionar port mapping: {e}")
                        return False
            
            print(f"❌ Serviço WANIPConnection não encontrado")
            return False
                
        except Exception as e:
            print(f"❌ Erro ao abrir porta: {e}")
            return False
    
    def closePort(self, port=9292, protocolo='TCP'):
        """Fecha uma porta no roteador"""
        
        if not self.dispositivo_conectado:
            print("⚠️  UPnP não configurado. Executando config()...")
            if not self.config():
                return False
        
        try:
            if not self.device:
                print("❌ Dispositivo não configurado")
                return False
            
            # Procurar pelo serviço de WANIPConnection ou WANPPPConnection
            services = self.device.get_services()
            for service in services:
                if 'WANIPConnection' in service.service_type or 'WANPPPConnection' in service.service_type:
                    try:
                        resultado = service.DeletePortMapping(
                            NewRemoteHost='',
                            NewExternalPort=str(port),
                            NewProtocol=protocolo.upper()
                        )
                        
                        print(f"✅ Porta {port}/{protocolo} fechada com sucesso!")
                        return True
                    except Exception as e:
                        print(f"❌ Erro ao deletar port mapping: {e}")
                        return False
            
            print(f"❌ Serviço WANIPConnection não encontrado")
            return False
                
        except Exception as e:
            print(f"❌ Erro ao fechar porta: {e}")
            return False

    def listPorts(self):
        """Lista todas as portas abertas via UPnP"""
        
        if not self.dispositivo_conectado:
            print("⚠️  UPnP não configurado. Executando config()...")
            if not self.config():
                return []
        
        try:
            if not self.device:
                print("❌ Dispositivo não configurado")
                return []
            
            portas_ativas = []
            services = self.device.get_services()
            
            for service in services:
                if 'WANIPConnection' in service.service_type or 'WANPPPConnection' in service.service_type:
                    try:
                        index = 0
                        print("\n📋 Portas abertas via UPnP:")
                        
                        while True:
                            try:
                                result = service.GetGenericPortMappingEntry(NewPortMappingIndex=index)
                                if not result:
                                    break
                                
                                info = {
                                    'porta_externa': result.get('NewExternalPort'),
                                    'protocolo': result.get('NewProtocol', 'TCP'),
                                    'ip_interno': result.get('NewInternalClient'),
                                    'porta_interna': result.get('NewInternalPort'),
                                    'descricao': result.get('NewPortMappingDescription', 'N/A'),
                                    'duracao': result.get('NewLeaseDuration')
                                }
                                portas_ativas.append(info)
                                print(f"  {index}: {info['porta_externa']}/{info['protocolo']} → "
                                      f"{info['ip_interno']}:{info['porta_interna']} ({info['descricao']})")
                                
                                index += 1
                            except:
                                break
                    except Exception as e:
                        print(f"⚠️  Erro ao listar portas: {e}")
            
            if not portas_ativas:
                print("  Nenhuma porta encontrada")
            
            return portas_ativas
            
        except Exception as e:
            print(f"❌ Erro ao listar portas: {e}")
            return []
    
    def getStatus(self):
        """Retorna o status atual do UPnP"""
        status = {
            'conectado': self.dispositivo_conectado,
            'ip_local': self.network.get_local_ip(),
            'ip_externo': self.network.get_external_ip()
        }
        
        print(f"\n📊 Status UPnP:")
        print(f"  Conectado: {'✅' if status['conectado'] else '❌'}")
        print(f"  IP Local: {status['ip_local']}")
        print(f"  IP Externo: {status['ip_externo'] or 'Não disponível'}")
        
        return status
    
    def quickTest(self, port=9292):
        """Teste rápido: abre a porta, lista e fecha"""
        print("\n" + "="*50)
        print("🚀 INICIANDO TESTE RÁPIDO UPnP")
        print("="*50)
        
        # Mostrar status inicial
        self.getStatus()
        
        # Configurar
        if not self.config():
            print("❌ Falha na configuração UPnP")
            return
        
        # Abrir porta
        self.openPort(port)
        
        # Listar portas
        self.listPorts()
        
        # Perguntar se quer fechar
        resposta = input(f"\n❓ Fechar porta {port}? (s/N): ")
        if resposta.lower() == 's':
            self.closePort(port)
            self.listPorts()
        
        print("\n" + "="*50)
        print("✅ TESTE FINALIZADO")
        print("="*50)

    def listPorts(self):
        """Lista todas as portas abertas via UPnP"""
        
        if not self.dispositivo_conectado:
            print("⚠️  UPnP não configurado. Executando config()...")
            if not self.config():
                return []
        
        try:
            print("\n📋 Portas abertas via UPnP:")
            
            index = 0
            portas_ativas = []
            tem_portas = False
            
            while True:
                try:
                    mapping = self.upnp.getgenericportmapping(index)
                    if mapping is None:
                        break
                    
                    tem_portas = True
                    info = {
                        'porta_externa': mapping[0],
                        'protocolo': mapping[1],
                        'ip_interno': mapping[2],
                        'porta_interna': mapping[3],
                        'descricao': mapping[4],
                        'duracao': mapping[5] if len(mapping) > 5 else None,
                        'index': index
                    }
                    portas_ativas.append(info)
                    
                    print(f"  {index}: {info['porta_externa']}/{info['protocolo']} → "
                            f"{info['ip_interno']}:{info['porta_interna']} ({info['descricao']})")
                    
                    index += 1
                except Exception as e:
                    # Se der erro em um índice específico, continua tentando
                    index += 1
                    continue
            
            if not tem_portas:
                print("  Nenhuma porta encontrada")
            
            return portas_ativas
            
        except Exception as e:
            print(f"❌ Erro ao listar portas: {e}")
            return []