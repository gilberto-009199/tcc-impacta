import logging
import os
import mmap
from typing import Optional, Tuple, BinaryIO

logger = logging.getLogger(__name__)

from app.util.MerkleyUtil import MerkleUtil

class FileUpload:
    def __init__(self, fileInfo = None):
        self.fileInfo = fileInfo
        self.upload = False
    def __str__(self):
        return f"FileUpload[upload={self.upload}, fileInfo={self.fileInfo}]"
    

