# karteapathconfig.py
import configparser
from pathlib import Path

from PySide6.QtCore import QDir, QDirIterator

from udescjoinvilletteagames.kartea.resources import resourceskartea_rc
from udescjoinvilletteautil import PathConfig


class KarteaPathConfig(PathConfig):
    """
    Configuração de caminhos específicos para o jogo KarTEA.

    - Recursos embutidos (imagens/sons padrão do jogo) -> Qt Resources (:/images/..., :/sounds/...)
    - Dados do usuário (imagens/sons personalizados, fases, jogadores, config) -> AppData
    """

    KARTEA_CONFIG_FILENAME = "kartea.ini"

    # ===================================================================
    # 1. CAMINHOS DE DADOS DO USUÁRIO (sempre em AppData)
    # ===================================================================
    KARTEA_DIR = PathConfig.EXERGAME_DIR / "kartea"  # .../exergames/kartea
    KARTEA_RESOURCES_DIR = KARTEA_DIR / "resources"  # .../kartea/resources
    KARTEA_IMAGES_DIR = (
        KARTEA_RESOURCES_DIR / "images"
    )  # imagens personalizadas
    KARTEA_SOUNDS_DIR = KARTEA_RESOURCES_DIR / "sounds"  # sons personalizados
    KARTEA_PHASES_DIR = KARTEA_RESOURCES_DIR / "phases"  # fases (se houver)
    KARTEA_PLAYER_DIR = KARTEA_DIR / "players"
    KARTEA_CONFIG_FILE = (
        KARTEA_DIR / KARTEA_CONFIG_FILENAME
    )  # .../kartea/kartea.ini

    # ===================================================================
    # 2. GARANTIA DE ESTRUTURA
    # ===================================================================
    @classmethod
    def ensure_kartea_dirs(cls) -> None:
        """Cria todas as pastas necessárias do KarTEA no AppData."""
        cls.ensure_user_dirs()
        for directory in [
            cls.KARTEA_DIR,
            cls.KARTEA_RESOURCES_DIR,
            cls.KARTEA_IMAGES_DIR,
            cls.KARTEA_SOUNDS_DIR,
            cls.KARTEA_PHASES_DIR,
            cls.KARTEA_PLAYER_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        cls.create_default_ini()

    # ===================================================================
    # 3. RECURSOS EMBUTIDOS (Qt Resource System)
    # ===================================================================
    @staticmethod
    def kartea_resource(path: str = "") -> str:
        return f":/kartea/{path}".rstrip("/")

    @staticmethod
    def kartea_image(name: str) -> str:
        """Recurso embutido (padrão do jogo)"""
        it = QDirIterator(
            ":/images",
            [name],  # Filtra pelo nome exato do arquivo
            QDir.Files,  # Apenas arquivos
            QDirIterator.Subdirectories,  # Busca recursiva em subpastas
        )

        if it.hasNext():
            path = it.next()
            return path
        else:
            return ""

    @staticmethod
    def kartea_sound(name: str) -> str:
        """Recurso embutido (padrão do jogo)"""
        it = QDirIterator(
            ":/sounds",
            [name],  # Filtra pelo nome exato do arquivo
            QDir.Files,  # Apenas arquivos
            QDirIterator.Subdirectories,  # Busca recursiva em subpastas
        )

        if it.hasNext():
            path = it.next()
            return path
        else:
            return ""

    @staticmethod
    def kartea_phases(name: str) -> str:
        """Recurso embutido (padrão do jogo)"""
        it = QDirIterator(
            ":/phases",
            [name],  # Filtra pelo nome exato do arquivo
            QDir.Files,  # Apenas arquivos
            QDirIterator.Subdirectories,  # Busca recursiva em subpastas
        )

        if it.hasNext():
            path = it.next()
            return path
        else:
            return ""

    # ===================================================================
    # 4. DADOS DO USUÁRIO
    # ===================================================================
    @classmethod
    def user_image(cls, filename: str) -> str:
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_IMAGES_DIR / filename)

    @classmethod
    def user_sound(cls, filename: str) -> str:
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_SOUNDS_DIR / filename)

    @classmethod
    def player(cls, filename: str) -> str:
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_PLAYER_DIR / filename)

    @classmethod
    def phase(cls, filename: str) -> str:
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_PHASES_DIR / filename)

    @classmethod
    def kartea_config(cls, filename: str = KARTEA_CONFIG_FILENAME) -> str:
        cls.ensure_kartea_dirs()
        return str(cls.KARTEA_DIR / filename)

    @classmethod
    def kartea_config_file_exists(
        cls, filename: str = KARTEA_CONFIG_FILENAME
    ) -> bool:
        """Verifica se o arquivo de configuração existe no diretório do usuário.

        Returns
        -------
        bool
            True se o arquivo config.ini existir, False caso contrário.
        """
        cls.ensure_user_dirs()  # Garante que as pastas existam (não cria o arquivo)
        config_path = Path(cls.kartea_config(filename))
        return config_path.exists()

    # ===================================================================
    # 5. LISTAGEM E CONFIG
    # ===================================================================
    @classmethod
    def list_images(cls) -> list[str]:
        cls.ensure_kartea_dirs()
        exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
        return sorted(
            [
                f.name
                for f in cls.KARTEA_IMAGES_DIR.iterdir()
                if f.is_file() and f.suffix.lower() in exts
            ]
        )

    @classmethod
    def list_sounds(cls) -> list[str]:
        cls.ensure_kartea_dirs()
        exts = {".wav", ".mp3", ".ogg", ".flac", ".aac"}
        return sorted(
            [
                f.name
                for f in cls.KARTEA_SOUNDS_DIR.iterdir()
                if f.is_file() and f.suffix.lower() in exts
            ]
        )

    @classmethod
    def read_config(cls) -> dict[str, dict[str, str]]:

        cls.ensure_kartea_dirs()
        config = configparser.ConfigParser()
        config.read(cls.KARTEA_CONFIG_FILE)
        return {
            section: dict(config[section]) for section in config.sections()
        }

    @classmethod
    def create_default_ini(cls) -> None:
        """
        Cria o arquivo kartea.ini com valores padrão caso ele não exista.
        Executado geralmente na primeira inicialização do sistema.
        """
        config_path = cls.KARTEA_CONFIG_FILE

        # Se já existe, não sobrescreve (preserva customizações do usuário)
        if config_path.exists():
            return

        config = configparser.ConfigParser(allow_no_value=True)

        # =============================================
        # Conteúdo padrão - valores iniciais do sistema
        # =============================================
        config["game_settings"] = {
            "phase_default": "1",
            "level_default": "1",
            "level_time_default": "120",
        }

        config["visual_resources"] = {
            "vehicle_image_default": "defaultvehicle",
            "environment_image_default": "defaultenvironment",
            "target_image_default": "defaultstar",
            "obstacle_image_default": "defaultobstacle",
        }

        config["visual_feedback"] = {
            "positive_feedback_image_default": "positive",
            "neutral_feedback_image_default": "neutral",
            "negative_feedback_image_default": "negative",
        }

        config["sound_feedback"] = {
            "positive_feedback_sound_default": "hit",
            "neutral_feedback_sound_default": "miss",
            "negative_feedback_sound_default": "error",
        }

        config["interface_settings"] = {
            "palette_default": "0",
            "hud_default": "true",
            "sound_default": "true",
        }

        # =============================================
        # Salva o arquivo com encoding UTF-8
        # =============================================
        with open(config_path, "w", encoding="utf-8") as configfile:
            config.write(configfile)

    @classmethod
    def list_builtin_vehicle_images(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para veículos embutidos"""

        result = []
        it = QDirIterator(
            ":/images/vehicle", QDir.Filter.Files, QDirIterator.Subdirectories
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_environment_images(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para ambientes embutidos"""

        result = []
        it = QDirIterator(
            ":/images/environment",
            QDir.Filter.Files,
            QDirIterator.Subdirectories,
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_obstacle_images(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para obstáculos embutidos"""

        result = []
        it = QDirIterator(
            ":/images/obstacle", QDir.Filter.Files, QDirIterator.Subdirectories
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_target_images(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para alvos embutidos"""

        result = []
        it = QDirIterator(
            ":/images/target", QDir.Filter.Files, QDirIterator.Subdirectories
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_feedback_positive_images(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para feedback positivo"""

        result = []
        it = QDirIterator(
            ":/images/feedback/positive",
            QDir.Filter.Files,
            QDirIterator.Subdirectories,
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_feedback_neutral_images(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para feedback positivo"""

        result = []
        it = QDirIterator(
            ":/images/feedback/neutral",
            QDir.Filter.Files,
            QDirIterator.Subdirectories,
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_feedback_negative_images(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para feedback positivo"""

        result = []
        it = QDirIterator(
            ":/images/feedback/negative",
            QDir.Filter.Files,
            QDirIterator.Subdirectories,
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_feedback_positive_sounds(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para feedback positivo"""

        result = []
        it = QDirIterator(
            ":/sounds/feedback/positive",
            QDir.Filter.Files,
            QDirIterator.Subdirectories,
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_feedback_neutral_sounds(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para feedback neutro"""

        result = []
        it = QDirIterator(
            ":/sounds/feedback/neutral",
            QDir.Filter.Files,
            QDirIterator.Subdirectories,
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser

    @classmethod
    def list_builtin_feedback_negative_sounds(cls) -> list[tuple[str, str]]:
        """Retorna [(display_name, resource_path), ...] para feedback negative"""

        result = []
        it = QDirIterator(
            ":/sounds/feedback/negative",
            QDir.Filter.Files,
            QDirIterator.Subdirectories,
        )
        while it.hasNext():
            path = it.next()
            name = it.fileName()
            result.append((name, path))
        return sorted(result)  # ou ordenar por outro critério se quiser
