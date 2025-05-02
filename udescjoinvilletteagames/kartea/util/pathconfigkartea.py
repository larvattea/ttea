import os
from pathlib import Path
from udescjoinvilletteautil.pathconfig import PathConfig

class PathConfigKartea(PathConfig):
    """Classe para configuração de caminhos de arquivos e diretórios do KarTEA."""
    
    kartea = os.path.join(PathConfig.games, "kartea")
    kartea_assets = os.path.join(kartea,"assets")
    kartea_images = os.path.join(kartea_assets, "images")
    kartea_sounds = os.path.join(kartea_assets, "sounds")
    kartea_phases = os.path.join(kartea, "phases")
    kartea_players = os.path.join(kartea, "players") 

    @classmethod
    def kartea_image(cls, filename): 
        """Retorna o caminho completo para um arquivo de imagem do KarTEA."""
        return os.path.join(cls.kartea_images, filename)
    
    @classmethod
    def kartea_sound(cls, filename): 
        """Retorna o caminho completo para um arquivo de som do KarTEA."""
        return os.path.join(cls.kartea_sounds, filename)
    
    @classmethod
    def kartea_player(cls, filename): 
        """Retorna o caminho completo para os arquivos de jogador do KarTEA."""
        return os.path.join(cls.kartea_players, filename)