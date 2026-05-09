import logging

logger = logging.getLogger(__name__)

from pathlib import Path

from app.util.MerkleyUtil import MerkleUtil
from app.util.FileUtil import FileUtil
from app.file.fileHandle import FileHandle

class FileManager():
    def __init__(self, app):
        logging.info(f"{__name__} iniciou!")
        self.app = app
        self.handles = {}

    def config(self):
        logging.info(f"{__name__} config iniciado!")
                
        if(hasattr(self.app,'fileManager')): 
            self.fileManager = self.app.fileManager

        if(hasattr(self.app, 'uiManager')): 
            self.uiManager = self.app.uiManager

        self.merkle = MerkleUtil()
        

    def run(self):
        logging.info(f"{__name__} run iniciado!")
        pass

    def stop(self):
        logging.info(f"{__name__} stop iniciado!")
        pass
    
    def addFile(self, name, path):
        logger.info("Name: "+ name)
        logger.info("Path: "+ path)
        self.merkle.load_file(path)
        self.merkle.build_tree()

        fileInfo = self.merkle.get_info()

        logger.info(f"file: {fileInfo}")
        
        self.handles[fileInfo.get('merkle_root')] = FileHandle(fileInfo=fileInfo)
        
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

        
        data = self.app.appData.getData()
        filesData = data.files.value

        filesData.append(fileInfo)
        data.files.on_next(filesData)
        
        # adicionar as menssagens de request das partes

        pass