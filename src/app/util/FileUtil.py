from pathlib import Path


class FileUtil:
    
    @staticmethod
    def criar_caminho_se_necessario(caminho):
        path = Path(caminho)
        
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"Diretórios criados: {path.parent}")
        
        if path.suffix and not path.exists():
            path.touch()
            print(f"Arquivo criado: {path.name}")