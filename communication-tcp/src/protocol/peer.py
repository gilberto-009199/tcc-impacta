class Peer:
    
    def __init__(self, socket, host, port, peerManager):
        self.socket = socket
        self.host = host
        self.port = port
        self.peerManager = peerManager

        self.identifier = None
        self.feature = None
        self.port = None
        self.info = None

        self.queueMsgRecv = []
        self.queueMsgSend = []

    def sendMsg(self, msg):
        self.queueMsgSend.append(msg);

    def recvMsg(self, msg):
        self.queueMsgRecv.append(msg);



    def run(self):
        # lifecycle
        pass


