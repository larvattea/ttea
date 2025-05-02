import os
from pathlib import Path

class PathConfig:
    """Classe para configuração de caminhos de arquivos e diretórios."""
    
    root = os.path.abspath(os.curdir)
    logfile = os.path.join(root, "log")
    players = os.path.join(root, "players")
    games = os.path.join(root, "udescjoinvilletteagames")
    assets = os.path.join(root, "assets")
    images = os.path.join(assets, "images")
    icons = os.path.join(assets, "icons")

    @classmethod
    def icon(cls, filename):
        """Retorna o caminho completo para um arquivo de ícone."""
        return os.path.join(cls.icons, filename)

    @classmethod
    def image(cls, filename):
        """Retorna o caminho completo para um arquivo de imagem."""
        return os.path.join(cls.images, filename)

    @classmethod
    def log(cls, filename):
        """Retorna o caminho completo para um arquivo de log."""
        return os.path.join(cls.logfile, filename)    
    
    @classmethod
    def player(cls, filename):
        """Retorna o caminho completo para um arquivo de jogador."""
        return os.path.join(cls.players, filename)    
    
    @classmethod
    def path_games(cls): 
        """Retorna o caminho dos jogos."""
        # Converte cls.games (string) em um objeto Path
        dirs = Path(cls.games)
        # Lista apenas os diretórios dentro de cls.games
        dirs = [d.name for d in dirs.iterdir() if d.is_dir()]
        return dirs
