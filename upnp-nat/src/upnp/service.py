import miniupnpc

from src.upnp.network import Network

class UPNPService:
    
    def __init__(self, app):
        """
        Inicializa o serviço UPnP com uma instância de Network
        
        Args:
            network: Instância da classe Network
        """
        self.network = Network()
        self.upnp = None
        self.dispositivo_conectado = False
        print("🔌 UPNPService initialized")
    
    def config(self):
        """Configura e descobre dispositivos UPnP na rede"""
        try:
            self.upnp = miniupnpc.UPnP()
            self.upnp.discoverdelay = 10000
            # Descobrir dispositivos (timeout de 2 segundos)
            print("🔍 Procurando dispositivos UPnP...")
            
            num_devices = self.upnp.discover();

            print(f"  Encontrados {num_devices} dispositivos")
            
            if num_devices == 0:
                print("❌ Nenhum dispositivo UPnP encontrado!")
                return False
            
            # Selecionar o gateway (roteador)
            self.upnp.selectigd()
            
            # Obter IP externo e atualizar o Network
            ip_externo = self.upnp.externalipaddress()
            self.network.set_external_ip(ip_externo)
            
            print(f"✅ UPnP configurado com sucesso!")
            print(f"  IP Local: {self.network.get_local_ip()}")
            print(f"  IP Externo: {self.network.get_external_ip()}")
            
            self.dispositivo_conectado = True
            return True
            
        except Exception as e:
            print(f"❌ Erro na configuração UPnP: {e}")
            return False
    
    def _porta_ja_existe(self, port, protocolo):
        """Verifica se uma porta já está mapeada"""
        try:
            # O argumento '0' significa listar todas as portas
            index = 0
            while True:
                try:
                    # Tenta obter o mapeamento no índice atual
                    mapping = self.upnp.getgenericportmapping(index)
                    if mapping is None:
                        break
                    
                    # Verifica se a porta e protocolo correspondem
                    if (mapping[0] == port and mapping[1] == protocolo):
                        return True, mapping
                    
                    index += 1
                except:
                    break
                    
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
                print(f"  {mapping[2]}:{mapping[3]} → {mapping[0]}/{mapping[1]}")
                return True
            
            # Adicionar mapeamento
            ip_local = self.network.get_local_ip()
            resultado = self.upnp.addportmapping(
                port,                    # Porta externa
                protocolo,                # Protocolo
                ip_local,                 # IP interno (do Network)
                port,                     # Porta interna
                descricao,                # Descrição
                ''                         # Remote host
            )
            
            if resultado:
                print(f"✅ Porta {port}/{protocolo} aberta com sucesso!")
                print(f"  {self.network.get_external_ip()}:{port} → {ip_local}:{port}")
                return True
            else:
                print(f"❌ Falha ao abrir porta {port}")
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
            resultado = self.upnp.deleteportmapping(port, protocolo)
            
            if resultado:
                print(f"✅ Porta {port}/{protocolo} fechada com sucesso!")
                return True
            else:
                print(f"❌ Falha ao fechar porta {port}/{protocolo}")
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
            portas = self.upnp.getgenericportmapping()
            
            print("\n📋 Portas abertas via UPnP:")
            if not portas or all(p is None for p in portas):
                print("  Nenhuma porta encontrada")
                return []
            
            portas_ativas = []
            for i, porta in enumerate(portas):
                if porta:
                    info = {
                        'porta_externa': porta[0],
                        'protocolo': porta[1],
                        'ip_interno': porta[2],
                        'porta_interna': porta[3],
                        'descricao': porta[4],
                        'duracao': porta[5] if len(porta) > 5 else None
                    }
                    portas_ativas.append(info)
                    print(f"  {i}: {info['porta_externa']}/{info['protocolo']} → "
                          f"{info['ip_interno']}:{info['porta_interna']} ({info['descricao']})")
            
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