import os

class PathConfig:
    """Classe para configuração de caminhos de arquivos e diretórios."""
    
    root = os.path.abspath(os.curdir)
    assets = os.path.join(root, "assets")
    images = os.path.join(assets, "images")
    icons = os.path.join(assets, "icons")
    logfile = os.path.join(root, "log")
    games = os.path.join(root, "udescjoinvilleipgames")
    kartea = os.path.join(games, "kartea")
    kartea_assets = os.path.join(kartea,"assets")
    kartea_images = os.path.join(kartea_assets, "images")
    karta_sounds = os.path.join(kartea_assets, "sounds")
    kartea_phases = os.path.join(kartea, "phases") 

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
    
    # @classmethod
    # def games(cls, filename): 
    #     pass

    @classmethod
    def kartea_images(cls, filename): 
        return os.path.join(cls.kartea_images, filename)
    
    @classmethod
    def kartea_sounds(cls, filename): 
        return os.path.join(cls.kartea_sounds, filename)