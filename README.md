# tcc-impacta

Produto final:
 + Interface grafica - src/app/ui/UIManager.py

   + Pagina de download e upload de arquivo - src/app/ui/page/homePage.py NOK
     + Permitir upload de um arquivo e gerar a arvore de merkley dele NOK
     + Gerar  hash verificador do arquivo e dos pices dele NOK
     + Avisar peers conectados de novos files NOK
   + Pagina de discover - src/app/ui/page/peerPage.py 
     + exibir pares do service discover OK
     + conectar com um par OK
     + permitir listar e  baixar um arquivo presento em um par conctado NOK
   + Pagina de config - src/app/ui/page/settingsPage.py
     + exibir ip interno e externo OK
     + ativar/desativar server do  src/app/peer/peerManager.py OK
     + ativar/desativar service discover do src/app/ssdp/SSDPManager.py OK
     + ativar/desativar service upnp do src/app/upnp/UPNPManager.py NOK

 + Centralizador do estado do aplicativo, usando reactive para visar de modificações - src/app/appData.py
 + Ponto de entrada src/app/application.py
 + Protocolo de rede -  src/app/peer/peerManager.py
   + packet MsgHandshake - src/app/peer/protocol/msg/msgHandShake.py OK
   + packet MsgInfo - src/app/peer/protocol/msg/msgInfo.py OK
   + packet MsgInfoRequest - src/app/peer/protocol/msg/msgInfoRequest.py OK
   + packet MsgKeepAlive - src/app/peer/protocol/msg/msgKeepAlive.py OK
   + packet MsgPiece - src/app/peer/protocol/msg/msgPiece.py OK
   + packet MsgPieceRequest - src/app/peer/protocol/msg/msgPieceRequest.py OK

 + Arvore de markov - src/app/file/fileManager.py NOK
   + Gerador do identificador do arquivo e hash dele e dos pieces  NOK
   + Verificar a integridade do arquivo  NOK

## Objetivo:

+ Sistema de download e upload de arquivos descentralizado 
+ Sistema de roteamento de arquivos entre pares KADAMELIA

## Arquitetura

 + UI MANAGER - src/app/ui/UIManager.py
 + PEER MANAGER - src/app/peer/peerManager.py
 + FILE MANAGER - src/app/upnp/UPNPManager.py
 + UPNP MANAGER - src/app/upnp/UPNPManager.py
 + SSDP MANAGER - src/app/ssdp/SSDPManager.py


# Como  desenvolver?

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install poetry flet
$ poetry lock
$ flet run -r main.py
```

# Como  rodar?

```bash
$ flet run
```

# Como buildar?

```bash
$ flet build linux -v
```


