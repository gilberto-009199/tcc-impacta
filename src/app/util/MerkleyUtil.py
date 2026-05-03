import logging

logger = logging.getLogger(__name__)

import hashlib
import os
from typing import List, Tuple, Optional


class MerkleUtil:
    """
    Utilitário para criar e validar Árvores de Merkle
    
    Uso básico:
        # Criar árvore
        merkle = MerkleUtil("meu_arquivo.pdf")
        merkle.build_tree()
        
        # Verificar arquivo todo
        merkle.verify_file("meu_arquivo.pdf")
        
        # Verificar bloco específico
        merkle.verify_block(5, dados_do_bloco, prova)
    """
    
    BLOCK_SIZE = 1024 * 1024  # 1 MB
    
    def __init__(self, file_path: str = None, block_size: int = BLOCK_SIZE):
        """
        Inicializa o utilitário
        
        Args:
            file_path: Caminho do arquivo (opcional)
            block_size: Tamanho do bloco em bytes (padrão: 1MB)
        """
        self.block_size = block_size
        self.file_path = file_path
        self.file_name = None
        self.file_size = 0
        self.total_blocks = 0
        self.blocks: List[bytes] = []  # Dados dos blocos
        self.block_hashes: List[str] = []  # SHA-1 de cada bloco
        self.merkle_root = None  # Raiz da árvore de Merkle
        self.file_hash = None  # SHA-1 do arquivo completo
        
        if file_path and os.path.exists(file_path):
            self.load_file(file_path)
    
    def load_file(self, file_path: str):
        """Carrega e divide o arquivo em blocos de 1MB"""
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        
        # Calcula quantos blocos serão necessários
        self.total_blocks = (self.file_size + self.block_size - 1) // self.block_size
        
        logger.info(f"\n📁 Arquivo: {self.file_name}")
        logger.info(f"   Tamanho: {self.file_size:,} bytes")
        logger.info(f"   Blocos: {self.total_blocks} blocos de {self.block_size:,} bytes")
        
        self.blocks = []
        self.block_hashes = []
        
        with open(file_path, 'rb') as f:
            block_index = 0
            while True:
                chunk = f.read(self.block_size)
                
                if not chunk:
                    break
                
                # Se for o último bloco e for menor que block_size, completa com zeros
                if len(chunk) < self.block_size:
                    chunk = chunk + b'\x00' * (self.block_size - len(chunk))
                
                self.blocks.append(chunk)
                block_index += 1
            
            # Garante que temos todos os blocos (caso arquivo vazio ou múltiplo exato)
            # Se o arquivo for exatamente múltiplo de block_size, não precisa completar
        
        # Calcula hash do arquivo completo
        with open(file_path, 'rb') as f:
            self.file_hash = hashlib.sha1(f.read()).hexdigest()
        
        logger.info(f"   🔑 SHA-1 do arquivo completo: {self.file_hash}...")
        
        return self.file_hash[:20]
    
    def _sha1(self, data: bytes) -> str:
        """Calcula SHA-1 de dados binários"""
        return hashlib.sha1(data).hexdigest()
    
    def _combine_hashes(self, left_hash: str, right_hash: str) -> str:
        """Combina dois hashes SHA-1"""
        combined = left_hash + right_hash
        return self._sha1(combined.encode('utf-8'))
    
    def build_tree(self) -> str:
        """
        Constrói a árvore de Merkle
        
        Returns:
            str: Raiz de Merkle (SHA-1 de 160 bits)
        """
        if not self.blocks:
            raise ValueError("Nenhum arquivo carregado. Use load_file() primeiro.")
        
        logger.info(f"\n🌳 Construindo árvore de Merkle...")
        
        # Calcula SHA-1 de cada bloco
        self.block_hashes = []
        for i, block in enumerate(self.blocks):
            block_hash = self._sha1(block)
            self.block_hashes.append(block_hash)
            logger.info(f"   Bloco {i:3d}: {block_hash}")
        
        # Constrói árvore recursivamente
        self.merkle_root = self._build_tree_recursive(self.block_hashes)
        
        logger.info(f"\n   🌿 Raiz de Merkle: {self.merkle_root}")
        logger.info(f"   🎯 Valor inteiro (Kademlia): {int(self.merkle_root, 16)}")
        
        return self.merkle_root
    
    def _build_tree_recursive(self, hashes: List[str]) -> str:
        """
        Constrói a árvore recursivamente
        
        Args:
            hashes: Lista de hashes do nível atual
            
        Returns:
            str: Hash da raiz
        """
        if len(hashes) == 1:
            return hashes[0]
        
        next_level = []
        
        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else left
            parent_hash = self._combine_hashes(left, right)
            next_level.append(parent_hash)
        
        return self._build_tree_recursive(next_level)
    
    def get_proof(self, block_index: int) -> List[Tuple[str, str]]:
        """
        Gera prova de Merkle para um bloco específico
        
        Args:
            block_index: Índice do bloco (0-based)
            
        Returns:
            List[Tuple[str, str]]: Lista de (hash, posicao) onde posicao é 'left' ou 'right'
        """
        if self.merkle_root is None:
            raise ValueError("Árvore não construída. Execute build_tree() primeiro.")
        
        if block_index < 0 or block_index >= self.total_blocks:
            raise IndexError(f"Bloco {block_index} inválido. Total: {self.total_blocks}")
        
        proof = []
        self._get_proof_recursive(self.block_hashes, block_index, proof)
        return proof
    
    def _get_proof_recursive(self, hashes: List[str], target_index: int, proof: List[Tuple[str, str]]):
        """Recupera a prova recursivamente"""
        if len(hashes) == 1:
            return
        
        next_level = []
        pairs = []
        
        # Cria pares e identifica onde está o target
        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else left
            parent_hash = self._combine_hashes(left, right)
            next_level.append(parent_hash)
            pairs.append((i, left, right, parent_hash))
        
        # Encontra em qual par está o target
        pair_index = target_index // 2
        start_idx = pair_index * 2
        left_hash = hashes[start_idx]
        right_hash = hashes[start_idx + 1] if start_idx + 1 < len(hashes) else left_hash
        
        # Adiciona o irmão à prova
        if target_index == start_idx:
            # Target está na esquerda, adiciona irmão direito
            proof.append((right_hash, 'right'))
        else:
            # Target está na direita, adiciona irmão esquerdo
            proof.append((left_hash, 'left'))
        
        # Continua para o próximo nível
        self._get_proof_recursive(next_level, pair_index, proof)
    
    def verify_block(self, block_index: int, block_data: bytes, proof: List[Tuple[str, str]]) -> bool:
        """
        Verifica se um bloco é válido
        
        Args:
            block_index: Índice do bloco
            block_data: Dados do bloco (pode ser menor que block_size)
            proof: Prova de Merkle gerada pelo provedor
            
        Returns:
            bool: True se o bloco é íntegro
        """
        # Completa o bloco com zeros se necessário
        if len(block_data) < self.block_size:
            block_data = block_data + b'\x00' * (self.block_size - len(block_data))
        
        # Calcula hash do bloco
        block_hash = self._sha1(block_data)
        
        # Reconstrói a raiz usando a prova
        computed_root = self._reconstruct_root(block_hash, proof)
        
        # Compara com a raiz esperada
        return computed_root == self.merkle_root
    
    def _reconstruct_root(self, leaf_hash: str, proof: List[Tuple[str, str]]) -> str:
        """Reconstrói a raiz a partir do hash da folha e da prova"""
        current_hash = leaf_hash
        
        for sibling_hash, position in proof:
            if position == 'left':
                current_hash = self._combine_hashes(sibling_hash, current_hash)
            else:  # 'right'
                current_hash = self._combine_hashes(current_hash, sibling_hash)
        
        return current_hash
    
    def verify_file(self, file_path: str = None) -> bool:
        """
        Verifica a integridade do arquivo completo
        
        Args:
            file_path: Caminho do arquivo (se None, usa o mesmo carregado)
            
        Returns:
            bool: True se o arquivo é íntegro
        """
        if file_path:
            verifier = MerkleUtil(file_path, self.block_size)
            verifier.build_tree()
            computed_root = verifier.merkle_root
            computed_hash = verifier.file_hash
        else:
            if not self.file_path:
                raise ValueError("Nenhum arquivo carregado")
            
            # Recalcula hash do arquivo
            with open(self.file_path, 'rb') as f:
                computed_hash = hashlib.sha1(f.read()).hexdigest()
            
            # Reconstrói a árvore
            computed_root = self._build_tree_recursive(self.block_hashes)
        
        is_valid = (computed_root == self.merkle_root and computed_hash == self.file_hash)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"VERIFICANDO INTEGRIDADE: {self.file_name}")
        logger.info(f"{'='*50}")
        logger.info(f"Hash do arquivo:")
        logger.info(f"  Esperado: {self.file_hash}")
        logger.info(f"  Calculado: {computed_hash}")
        logger.info(f"  ✅ Hash confere" if computed_hash == self.file_hash else "  ❌ Hash DIFERENTE")
        logger.info(f"\nRaiz de Merkle:")
        logger.info(f"  Esperado: {self.merkle_root}")
        logger.info(f"  Calculado: {computed_root}")
        logger.info(f"  ✅ Raiz confere" if computed_root == self.merkle_root else "  ❌ Raiz DIFERENTE")
        
        if is_valid:
            logger.info(f"\n✅ ARQUIVO ÍNTEGRO!")
        else:
            logger.info(f"\n❌ ARQUIVO CORROMPIDO!")
        
        return is_valid
    
    def verify_blocks(self, block_indices: List[int], 
                     block_data_list: List[bytes],
                     proofs: List[List[Tuple[str, str]]]) -> List[int]:
        """
        Verifica múltiplos blocos
        
        Args:
            block_indices: Lista de índices dos blocos
            block_data_list: Lista de dados dos blocos
            proofs: Lista de provas correspondentes
            
        Returns:
            List[int]: Lista de índices dos blocos inválidos
        """
        invalid_blocks = []
        
        for i, (idx, data, proof) in enumerate(zip(block_indices, block_data_list, proofs)):
            if not self.verify_block(idx, data, proof):
                invalid_blocks.append(idx)
                logger.info(f"❌ Bloco {idx}: INVÁLIDO")
            else:
                logger.info(f"✅ Bloco {idx}: válido")
        
        return invalid_blocks
    
    def get_info(self) -> dict:
        """Retorna informações do arquivo e árvore"""
        return {
            "name": self.file_name,
            "path": self.file_path,
            "size": self.file_size,
            "hash": self.file_hash,
            "block_size": self.block_size,
            "total_blocks": self.total_blocks,
            "merkle_root": self.merkle_root,
            "block_hashes": self.block_hashes,
            "bytes_download": 0,
            "bytes_upload": 0,
            "total_pares": 0
        }
    
    def print_tree(self):
        """Exibe a árvore de Merkle de forma hierárquica"""
        if not self.block_hashes:
            logger.info("Árvore não construída")
            return
        
        logger.info(f"\n{'='*50}")
        logger.info(f"ÁRVORE DE MERKLE - {self.file_name}")
        logger.info(f"{'='*50}")
        
        # Nível das folhas (blocos)
        logger.info(f"\n📄 FOLHAS (SHA-1 de cada bloco):")
        for i, h in enumerate(self.block_hashes):
            logger.info(f"   Bloco {i:3d}: {h}")
        
        # Reconstrói níveis para exibição
        levels = [self.block_hashes]
        current = self.block_hashes
        
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                parent = self._combine_hashes(left, right)
                next_level.append(parent)
            levels.append(next_level)
            current = next_level
        
        # Exibe níveis internos
        for level_idx, level in enumerate(levels[1:-1], 1):
            logger.info(f"\n🌿 NÍVEL {level_idx}:")
            for i, h in enumerate(level):
                logger.info(f"   Nó {i:3d}: {h}")
        
        # Raiz
        logger.info(f"\n🌟 RAIZ DE MERKLE:")
        logger.info(f"   {levels[-1][0]}")


# ============ FUNÇÕES DE USO RÁPIDO ============

def criar_arvore_merkle(arquivo: str) -> MerkleUtil:
    """
    Função rápida para criar árvore de Merkle de um arquivo
    
    Args:
        arquivo: Caminho do arquivo
        
    Returns:
        MerkleUtil: Instância com a árvore construída
    """
    util = MerkleUtil(arquivo)
    util.build_tree()
    return util


def verificar_arquivo(arquivo: str, merkle_root_esperada: str = None) -> bool:
    """
    Verifica integridade de um arquivo
    
    Args:
        arquivo: Caminho do arquivo
        merkle_root_esperada: Raiz de Merkle esperada (opcional)
        
    Returns:
        bool: True se íntegro
    """
    util = MerkleUtil(arquivo)
    util.build_tree()
    
    if merkle_root_esperada:
        if util.merkle_root != merkle_root_esperada:
            logger.info(f"❌ Raiz de Merkle não confere!")
            return False
    
    return util.verify_file()

"""
# ============ EXEMPLOS DE USO ============

if __name__ == "__main__":
    
    # Criando arquivo de exemplo
    logger.info("\n" + "="*60)
    logger.info("CRIANDO ARQUIVO DE EXEMPLO")
    logger.info("="*60)
    
    # Arquivo de 2.5 MB (3 blocos: 1MB + 1MB + 0.5MB completado com zeros)
    with open("exemplo.bin", "wb") as f:
        f.write(b"A" * 1024 * 1024)  # Bloco 1: 1MB de 'A'
        f.write(b"B" * 1024 * 1024)  # Bloco 2: 1MB de 'B'
        f.write(b"C" * 512 * 1024)   # Bloco 3: 0.5MB de 'C' (será completado)
    
    # ============ EXEMPLO 1: Criar árvore ============
    logger.info("\n" + "="*60)
    logger.info("EXEMPLO 1: CRIANDO ÁRVORE DE MERKLE")
    logger.info("="*60)
    
    merkle = MerkleUtil("exemplo.bin")
    root = merkle.build_tree()
    
    # Exibe informações
    info = merkle.get_info()
    logger.info(f"\n📊 INFORMAÇÕES:")
    logger.info(f"   Arquivo: {info['file_name']}")
    logger.info(f"   Tamanho: {info['file_size']:,} bytes")
    logger.info(f"   SHA-1 do arquivo: {info['file_hash']}")
    logger.info(f"   Raiz de Merkle: {info['merkle_root']}")
    logger.info(f"   Total de blocos: {info['total_blocks']}")
    
    # Exibe árvore completa
    merkle.print_tree()
    
    # ============ EXEMPLO 2: Verificar arquivo todo ============
    logger.info("\n" + "="*60)
    logger.info("EXEMPLO 2: VERIFICANDO ARQUIVO COMPLETO")
    logger.info("="*60)
    
    # Verifica arquivo original (deve ser válido)
    merkle.verify_file()
    
    # Simula corrupção e verifica
    logger.info("\n" + "-"*40)
    logger.info("SIMULANDO CORRUPÇÃO NO ARQUIVO")
    logger.info("-"*40)
    
    with open("exemplo_corrupto.bin", "wb") as f:
        with open("exemplo.bin", "rb") as orig:
            data = orig.read()
            # Corrompe byte 100
            data = data[:100] + b'X' + data[101:]
            f.write(data)
    
    merkle_corrupto = MerkleUtil("exemplo_corrupto.bin")
    merkle_corrupto.build_tree()
    merkle_corrupto.verify_file()
    
    # ============ EXEMPLO 3: Verificar bloco específico ============
    logger.info("\n" + "="*60)
    logger.info("EXEMPLO 3: VERIFICANDO BLOCO ESPECÍFICO")
    logger.info("="*60)
    
    # Obtém prova para o bloco 1
    proof_block1 = merkle.get_proof(1)
    logger.info(f"\nProva para o Bloco 1:")
    for i, (h, pos) in enumerate(proof_block1):
        logger.info(f"   Nível {i}: {pos} - {h[:20]}...")
    
    # Verifica bloco 1
    block1_data = merkle.blocks[1]
    is_valid = merkle.verify_block(1, block1_data, proof_block1)
    logger.info(f"\nVerificando Bloco 1: {'✅ Válido' if is_valid else '❌ Inválido'}")
    
    # Simula corrupção no bloco
    logger.info(f"\nSimulando corrupção no Bloco 1:")
    corrupted_block = block1_data[:100] + b'X' + block1_data[101:]
    is_valid = merkle.verify_block(1, corrupted_block, proof_block1)
    logger.info(f"Bloco 1 corrompido: {'✅ Válido' if is_valid else '❌ Inválido'}")
    
    # ============ EXEMPLO 4: Arquivo menor que 1MB ============
    logger.info("\n" + "="*60)
    logger.info("EXEMPLO 4: ARQUIVO MENOR QUE 1MB")
    logger.info("="*60)
    
    # Arquivo pequeno (500KB)
    with open("pequeno.txt", "wb") as f:
        f.write(b"Conteudo pequeno" * 10000)  # ~170KB
    
    merkle_pequeno = MerkleUtil("pequeno.txt")
    root_pequeno = merkle_pequeno.build_tree()
    
    logger.info(f"\nArquivo pequeno: {merkle_pequeno.file_size:,} bytes")
    logger.info(f"Total de blocos: {merkle_pequeno.total_blocks}")
    logger.info(f"Bloco único completado com zeros até 1MB")
    logger.info(f"Raiz de Merkle: {root_pequeno}")
    
    # ============ EXEMPLO 5: Funções rápidas ============
    logger.info("\n" + "="*60)
    logger.info("EXEMPLO 5: FUNÇÕES RÁPIDAS")
    logger.info("="*60)
    
    # Criar árvore com uma linha
    util = criar_arvore_merkle("exemplo.bin")
    logger.info(f"\n✅ Árvore criada! Raiz: {util.merkle_root[:20]}...")
    
    # Verificar arquivo
    eh_valido = verificar_arquivo("exemplo.bin")
    
    logger.info("\n" + "="*60)
    logger.info("✅ UTILITÁRIO PRONTO PARA USO!")
    logger.info("="*60)

"""