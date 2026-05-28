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
        self.pieces_received = {}

    def addBlock(self, block_index, block_size, buffer):
        self.pieces_received[block_index] = (block_size, buffer)
        self.fileInfo.get('block_download')[block_index] = 1

    def __str__(self):
        return f"FileDownload[download={self.download}, fileInfo={self.fileInfo}]"