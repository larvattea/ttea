import os

class PathConfig:
    """Classe para configuração de caminhos de arquivos e diretórios."""
    
    root = os.path.abspath(os.curdir)
    assets = os.path.join(root, "assets")
    images = os.path.join(assets, "images")
    icons = os.path.join(assets, "icons")
    logfile = os.path.join(root, "log")

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