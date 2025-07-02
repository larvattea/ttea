from pathlib import Path
from typing import List


class PathConfig:
    """Classe para configuração de caminhos de arquivos e diretórios."""

    root = Path.cwd()
    log_dir = root / "log"
    players_dir = root / "players"
    games_dir = root / "udescjoinvilletteagames"
    assets_dir = root / "assets"
    translations_dir = root/"translations"
    images_dir = assets_dir / "images"
    icons_dir = assets_dir / "icons"
    helps_dir = root / "help"
    helps_dir_pt = helps_dir / "pt"

    @classmethod
    def _create_directories(cls) -> None:
        """Cria todos os diretórios necessários se não existirem."""
        for directory in [
            cls.players_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def icon(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de ícone.

        Args:
            filename: Nome do arquivo de ícone.

        Returns:
            Caminho completo para o arquivo de ícone.
        """
        return str(cls.icons_dir / filename)

    @classmethod
    def image(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de imagem.

        Args:
            filename: Nome do arquivo de imagem.

        Returns:
            Caminho completo para o arquivo de imagem.
        """
        return str(cls.images_dir / filename)

    @classmethod
    def log(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de log.

        Args:
            filename: Nome do arquivo de log.

        Returns:
            Caminho completo para o arquivo de log.
        """
        return str(cls.log_dir / filename)

    @classmethod
    def player(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de jogador.

        Args:
            filename: Nome do arquivo de jogador.

        Returns:
            Caminho completo para o arquivo de jogador.
        """
        return str(cls.players_dir / filename)
    
    @classmethod
    def translation(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de tradução.

        Args:
            filename: Nome do arquivo de tradução.

        Returns:
            Caminho completo para o arquivo de tradução.
        """
        return str(cls.translations_dir / filename)
    
    @classmethod
    def inifile(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de ini no raiz.

        Args:
            filename: Nome do arquivo de ini.

        Returns:
            Caminho completo para o arquivo de ini.
        """
        return str(cls.root / filename)

    @classmethod
    def path_games(cls) -> List[str]:
        """Retorna uma lista com os nomes dos diretórios de jogos.

        Returns:
            Lista com os nomes dos diretórios dentro do diretório de jogos.

        Raises:
            FileNotFoundError: Se o diretório de jogos não existir.
        """
        cls._create_directories()
        return [d.name for d in cls.games_dir.iterdir() if d.is_dir() and d.name != "__pycache__"]
    
    @classmethod
    def path_help_pt(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de help.

        Args:
            filename: Nome do arquivo de help.

        Returns:
            Caminho completo para o arquivo de tradução.
        """
        return str(cls.helps_dir_pt / filename)