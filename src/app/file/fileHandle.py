import logging
import os
import mmap
from typing import Optional, Tuple, BinaryIO

logger = logging.getLogger(__name__)

from app.util.MerkleyUtil import MerkleUtil

class FileHandle:
    """Gerencia a conexão com um arquivo aberto"""
    def __init__(self, fileInfo = None):
        self.fileInfo = fileInfo
        self.path = fileInfo.get('path')
        self.size = fileInfo.get('size')
        self.file: Optional[BinaryIO] = None
        self.mmap: Optional[mmap.mmap] = None
        self._open()
    
    def _open(self):
        """Abre o arquivo e cria mapeamento de memória"""
        self.file = open(self.path, 'rb')
        
        # Obtém o tamanho real do arquivo
        try:
            real_size = os.path.getsize(self.path)
            self.size = real_size
        except OSError as e:
            logger.error(f"Erro ao obter tamanho do arquivo {self.path}: {e}")
            self.size = 0
        
        # Verifica se o arquivo tem 0 bytes
        if self.size == 0:
            logger.info(f"Arquivo {self.path} tem 0 bytes (arquivo vazio/criado recentemente)")
            # Não tenta criar mmap para arquivo vazio
            self.mmap = None
            return
        
        try:
            # Tenta usar mmap para acesso eficiente (apenas para arquivos > 0 bytes)
            self.mmap = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        except Exception as e:
            logger.warning(f"Falha ao criar mmap para {self.path}: {e}")
            self.mmap = None
    
    def read_block(self, block_index: int, block_size: int = 1024 * 1024) -> Optional[bytes]:
        """
        Lê um bloco arbitrário do arquivo
        
        Args:
            block_index: Índice do bloco (0-based)
            block_size: Tamanho do bloco em bytes (padrão: 1MB)
        
        Returns:
            bytes do bloco ou None se índice inválido
        """
        # Se o arquivo tem 0 bytes, retorna None ou bytes vazio baseado na necessidade
        if self.size == 0:
            logger.debug(f"Arquivo vazio (0 bytes), não é possível ler bloco {block_index}")
            return None
        
        offset = block_index * block_size
        
        if offset >= self.size:
            return None
        
        # Calcula o tamanho real do bloco (pode ser menor no último bloco)
        actual_size = min(block_size, self.size - offset)
        
        if self.mmap:
            # Leitura eficiente via mmap
            return self.mmap[offset:offset + actual_size]
        else:
            # Fallback para leitura tradicional
            self.file.seek(offset)
            return self.file.read(actual_size)
    
    def get_block_count(self, block_size: int = 1024 * 1024) -> int:
        """Retorna o número total de blocos de 1MB no arquivo"""
        if self.size == 0:
            return 0
        return (self.size + block_size - 1) // block_size
    
    def get_block_range(self, start_block: int, end_block: int, block_size: int = 1024 * 1024) -> Optional[bytes]:
        """
        Lê um range contínuo de blocos
        
        Args:
            start_block: Bloco inicial (inclusivo)
            end_block: Bloco final (exclusivo)
            block_size: Tamanho de cada bloco
        
        Returns:
            bytes concatenados dos blocos
        """
        if self.size == 0:
            logger.debug("Arquivo vazio (0 bytes), retornando bytes vazio")
            return b''  # Retorna bytes vazio para arquivo vazio
        
        if start_block >= end_block:
            return None
        
        result = bytearray()
        for block_idx in range(start_block, end_block):
            block_data = self.read_block(block_idx, block_size)
            if block_data is None:
                break
            result.extend(block_data)
        
        return bytes(result)
    
    def is_empty(self) -> bool:
        """Verifica se o arquivo está vazio (0 bytes)"""
        return self.size == 0
    
    def get_size_mb(self) -> float:
        """Retorna o tamanho do arquivo em MB"""
        return self.size / (1024 * 1024)
    
    def close(self):
        """Fecha a conexão com o arquivo"""
        if self.mmap:
            self.mmap.close()
        if self.file:
            self.file.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

