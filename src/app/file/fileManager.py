import threading
import time

import logging

from app.peer.protocol.msg.msgPiece import MsgPiece
from app.peer.protocol.msg.msgPieceRequest import MsgPieceRequest

logger = logging.getLogger(__name__)

from pathlib import Path

from app.util.MerkleyUtil import MerkleUtil, BLOCK_SIZE
from app.util.FileUtil import FileUtil
from app.file.fileHandle import FileHandle
from app.file.fileUpload import FileUpload
from app.file.fileDownload import FileDownload


class FileManager():
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app
        self.handles = {}
        self.uploads = {}
        self.downloads = {}
        self.running = False

    def getDownload(self, fileInfo):
        return self.downloads[fileInfo.get('merkle_root')]
    
    def setDownload(self, fileInfo):
        self.downloads[fileInfo.get('merkle_root')]
    
    def getUpload(self, fileInfo):
        return self.uploads[fileInfo.get('merkle_root')]
    
    def setUpload(self, fileInfo):
        self.uploads[fileInfo.get('merkle_root')]

    def config(self):
        logging.info(f"{__name__} config iniciado!")
                
        if(hasattr(self.app,'peerManager')): 
            self.peerManager = self.app.peerManager

        if(hasattr(self.app, 'uiManager')): 
            self.uiManager = self.app.uiManager

        self.merkle = MerkleUtil()
        
        if len(self.handles) > 0:
            self.run()

    def run(self):
        logging.info(f"{__name__} run iniciado!")
        try:

            if self.running:
                logger.info(f"[SERVIDOR] Já está rodando")
                return
            self.running = True
            self.thread = threading.Thread(target=self.serve, daemon=False)
            self.thread.start()

        except Exception as e:
            logger.warning(f"Falha no fileManager.run() {e}")
    
    def serve(self):
        # queue Pieces in files to peerManager and update statics
        # verify Pieces  and update statics
        while self.running:
            try:

                self.verifyPieces()
                time.sleep(0.1)
                self.requestPieces()
                time.sleep(0.1)
                self.sendPieces()

            except BlockingIOError:
                pass
            except Exception as e:
                logger.info(f"78 [FileManager] Erro ao executar FileManager: {e}")
                tb = e.__traceback__
                
                while tb.tb_next:
                    tb = tb.tb_next
                
                linha = tb.tb_lineno
                arquivo = tb.tb_frame.f_code.co_filename
                logger.info(f"[FileManager] Erro no arquivo: {arquivo}, linha: {linha}, erro: {e}")

    def verifyPieces(self):
        logging.debug(f"{__name__} verifyPieces iniciado!")
        try:

            for merkle_root in self.downloads:
                fileDownload = self.downloads[merkle_root]
                if not fileDownload.download:
                    continue

                fileInfo = fileDownload.fileInfo
                block_hashes = fileInfo.get('block_hashes')
                block_download = fileInfo.get('block_download')

                for index, block in enumerate(block_download):
                    if block == 0:
                        continue
                    
                    block_size, buffer = fileDownload.pieces_received.get(index, (None, None))
                    if block_size is None or buffer is None:
                        logger.warning(f"Bloco {index} não encontrado em pieces_received para {merkle_root}")
                        continue

                    # @todo verify block hash with block_hashes[index]
                    # if hash(buffer) == block_hashes[index]:
                    #     fileDownload.block_download[index] = 1
                    #     logger.info(f"Bloco {index} verificado com sucesso para {merkle_root}")
                    # else:
                    #     logger.warning(f"Falha na verificação do bloco {index} para {merkle_root}, hash não corresponde")


        except Exception as e:
            tb = e.__traceback__
            
            while tb.tb_next:
                tb = tb.tb_next
            
            linha = tb.tb_lineno
            arquivo = tb.tb_frame.f_code.co_filename
            logger.info(f"[FileManager] Erro no arquivo: {arquivo}, linha: {linha}, erro: {e}")



    def requestPieces(self):
        logging.debug(f"{__name__} requestPieces iniciado!")
        for merkle_root in self.downloads:
            fileDownload = self.downloads[merkle_root]
            if not fileDownload.download:
                continue

            fileInfo = fileDownload.fileInfo
            merkle_root = fileInfo.get('merkle_root')
            block_size = fileInfo.get('block_size')
            total_blocks = fileInfo.get('total_blocks')
            block_hashes = fileInfo.get('block_hashes')
            block_download = fileInfo.get('block_download')

            logging.debug(f"{__name__} requestPieces pieces to block_size={block_size}, total_blocks={total_blocks}, block_hashes={block_hashes}, block_download={block_download}")

            for index, block in enumerate(block_download):
                if block == 0:
                    self.peerManager.requestPieces(merkle_root, index, block_size)



    def sendPieces(self):
        logging.debug(f"{__name__} sendPieces iniciado!")



    def stop(self):
        logging.info(f"{__name__} stop iniciado!")
        self.running = False
    
    def addFile(self, name, path):
        logger.info("Name: "+ name)
        logger.info("Path: "+ path)
        self.merkle.load_file(path)
        self.merkle.build_tree()

        fileInfo = self.merkle.get_info()

        logger.info(f"file: {fileInfo}")
        
        self.handles[fileInfo.get('merkle_root')] = FileHandle(fileInfo=fileInfo)
        self.uploads[fileInfo.get('merkle_root')] = FileUpload(fileInfo=fileInfo)
        self.downloads[fileInfo.get('merkle_root')] = FileDownload(fileInfo=fileInfo)

        data = self.app.appData.getData()
        filesData = data.files.value

        filesData.append(fileInfo)
        data.files.on_next(filesData)
        
        return fileInfo
    
    def addFileDownload(self, fileInfo, path):
        logging.info(f"{__name__} addDownloadFile iniciado! fileInfo={fileInfo}, path={path}")
        # criar arquivo e camnho s en existir em path
        
        FileUtil.criar_caminho_se_necessario(path)
        
        # replace path in fileInfo.path
        fileInfo['path'] = path
        fileInfo["block_download"] = [0] * len(fileInfo['block_hashes'])

        self.handles[fileInfo.get('merkle_root')] = FileHandle(fileInfo=fileInfo)
        self.uploads[fileInfo.get('merkle_root')] = FileUpload(fileInfo=fileInfo)
        self.downloads[fileInfo.get('merkle_root')] = FileDownload(fileInfo=fileInfo)
        
        data = self.app.appData.getData()
        filesData = data.files.value

        filesData.append(fileInfo)
        data.files.on_next(filesData)

        self.config()

    def sendMsgPiece(self, peer, merkle_root, piece, index, buffer_length):
        logging.info(f"{__name__} sendMsgPiece iniciado! peer={peer}, merkle_root={merkle_root}, piece={piece}, index={index}, buffer_length={buffer_length}")

        handle = self.handles[merkle_root];
        # @todo calc buffer_length based on piece and index
        buffer = handle.read_block(block_index=index, block_size=buffer_length)
        msg = MsgPiece(
            identifier_file = merkle_root,
            identifier_piece = piece,
            identifier_index = index,
            buffer = buffer
        )
        peer.queueSend(msg)

    def recvMsgPiece(self, peer, merkle_root, identifier_piece, identifier_index, buffer):
        logging.info(f"{__name__} recvMsgPiece iniciado! peer={peer}, merkle_root={merkle_root}, identifier_piece={identifier_piece}, identifier_index={identifier_index}, buffer_length={len(buffer)}")

        download = self.downloads[merkle_root];
        download.addBlock(block_index=identifier_piece * BLOCK_SIZE, block_size=len(buffer), buffer=buffer)