import os
from pathlib import Path

from udescjoinvilletteautil.pathconfig import PathConfig


class KarteaPathConfig(PathConfig):
    """Classe para configuração de caminhos de arquivos e diretórios do KarTEA."""

    kartea_dir = PathConfig.games_dir / "kartea"
    kartea_assets_dir = kartea_dir / "assets"
    kartea_images_dir = kartea_assets_dir / "images"
    kartea_sounds_dir = kartea_assets_dir / "sounds"
    kartea_phases_dir = kartea_dir / "phases"
    kartea_players_dir = kartea_dir / "players"

    @classmethod
    def create_directories(cls) -> None:
        """Cria todos os diretórios necessários do KarTEA se não existirem."""
        for directory in [
            cls.kartea_players_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def kartea_image(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de imagem do KarTEA.

        Args:
            filename: Nome do arquivo de imagem.

        Returns:
            Caminho completo para o arquivo de imagem.
        """
        cls.create_directories()
        return str(cls.kartea_images_dir / filename)

    @classmethod
    def kartea_sound(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de som do KarTEA.

        Args:
            filename: Nome do arquivo de som.

        Returns:
            Caminho completo para o arquivo de som.
        """
        cls.create_directories()
        return str(cls.kartea_sounds_dir / filename)

    @classmethod
    def kartea_player(cls, filename: str) -> str:
        """Retorna o caminho completo para um arquivo de jogador do KarTEA.

        Args:
            filename: Nome do arquivo de jogador.

        Returns:
            Caminho completo para o arquivo de jogador.
        """
        cls.create_directories()
        return str(cls.kartea_players_dir / filename)
