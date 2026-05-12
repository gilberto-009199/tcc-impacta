import logging
import os
import mmap
from typing import Optional, Tuple, BinaryIO

logger = logging.getLogger(__name__)

from app.util.MerkleyUtil import MerkleUtil

class FileDownload:
    def __init__(self, fileInfo = None):
        self.fileInfo = fileInfo
        self.download = False
    def __str__(self):
        return f"FileDownload[download={self.download}, fileInfo={self.fileInfo}]"