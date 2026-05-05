import sys
from pathlib import Path
from typing import List

from platformdirs import user_data_dir


class PathConfig:
    """
    Centralizador de caminhos da aplicação.

    - Suporte completo a PyInstaller e modo desenvolvimento
    """

    APP_NAME = "ttea"
    APP_AUTHOR = "udesc"

    CONFIG_FILENAME = "config.ini"
    CALIBRATION_FILENAME = "calibration.ini"

    # ===================================================================
    # Diretório base
    # ===================================================================
    if getattr(sys, "frozen", False):
        BASE_DIR: Path = Path(user_data_dir(APP_NAME, APP_AUTHOR))
        EXERGAME_DIR: Path = BASE_DIR / "exergames"
    else:
        BASE_DIR: Path = Path(__file__).parent.parent
        EXERGAME_DIR: Path = BASE_DIR / "udescjoinvilletteagames"
        BASE_DIR: Path = BASE_DIR / "data"

    # Subdiretórios — adicione aqui novas pastas
    CONFIG_DIR: Path = BASE_DIR / "config"
    CALIBRATION_DIR: Path = BASE_DIR / "calibration"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    INSTITUTIONFACILITY_DIR: Path = BASE_DIR / "institutionfacilities"
    LOG_DIR: Path = BASE_DIR / "log"
    MODELS_DIR: Path = BASE_DIR / "mediapipemodels"
    PLAYERS_DIR: Path = BASE_DIR / "players"
    PROFESSIONAL_DIR: Path = BASE_DIR / "professionals"

    # ===================================================================
    # Recursos embutidos (Qt)
    # ===================================================================
    @staticmethod
    def resource(path: str = "") -> str:
        return f":/{path}".rstrip("/")

    @staticmethod
    def icon_system(name: str) -> str:
        return f":/icons/system/{name}"

    @staticmethod
    def icon_ui_button(name: str) -> str:
        return f":/icons/ui/buttons/{name}"

    @staticmethod
    def icon_ui_menu(name: str) -> str:
        return f":/icons/ui/menu/{name}"

    @staticmethod
    def flag(name: str) -> str:
        return f":/flags/{name}"

    @staticmethod
    def image(name: str) -> str:
        return f":/images/{name}"

    @staticmethod
    def ui(name: str) -> str:
        return f":/ui/{name}"

    @staticmethod
    def translation(name: str) -> str:
        return f":/translations/{name}"

    @staticmethod
    def sounds(name: str) -> str:
        return f":/sounds/{name}"

    @staticmethod
    def help(path: str = "") -> str:
        return f":/help/{path}".rstrip("/")

    # ===================================================================
    # Introspecção automática
    # ===================================================================
    @classmethod
    def _get_dir_names(cls) -> List[str]:
        """Retorna nomes de todos os atributos que terminam com _DIR"""
        return [
            name
            for name in vars(cls)
            if name.endswith("_DIR") and not name.startswith("_")
        ]

    @classmethod
    def _get_user_dirs(cls) -> List[Path]:
        """Retorna os objetos Path dos diretórios"""
        return [
            value
            for name, value in vars(cls).items()
            if name.endswith("_DIR") and not name.startswith("_")
        ]

    # ===================================================================
    # Métodos de dados do usuário
    # ===================================================================
    @classmethod
    def ensure_dirs(cls) -> None:
        """Cria todos os diretórios automaticamente."""
        for directory in cls._get_user_dirs():
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _user_file(cls, directory: Path, filename: str) -> str:
        cls.ensure_dirs()
        return str(directory / filename)

    @classmethod
    def config(cls, filename: str = CONFIG_FILENAME) -> str:
        return cls._user_file(cls.CONFIG_DIR, filename)

    @classmethod
    def calibration(cls, filename: str = CALIBRATION_FILENAME) -> str:
        return cls._user_file(cls.CALIBRATION_DIR, filename)

    @classmethod
    def professional(cls, filename: str) -> str:
        return cls._user_file(cls.PROFESSIONAL_DIR, filename)

    @classmethod
    def institutionfacility(cls, filename: str) -> str:
        return cls._user_file(cls.INSTITUTIONFACILITY_DIR, filename)

    @classmethod
    def player(cls, filename: str) -> str:
        return cls._user_file(cls.PLAYERS_DIR, filename)

    @classmethod
    def model(cls, filename: str) -> str:
        return cls._user_file(cls.MODELS_DIR, filename)

    @classmethod
    def export(cls, filename: str) -> str:
        return cls._user_file(cls.EXPORTS_DIR, filename)

    @classmethod
    def log(cls, filename: str) -> str:
        return cls._user_file(cls.LOG_DIR, filename)

    @classmethod
    def game_save(cls, game_name: str, filename: str) -> str:
        cls.ensure_dirs()
        game_dir = cls.EXERGAME_DIR / game_name
        game_dir.mkdir(exist_ok=True)
        return str(game_dir / filename)

    # ===================================================================
    # Suporte a testes
    # ===================================================================
    @classmethod
    def set_base_dir(cls, path: str | Path) -> None:
        """Altera o diretório base (útil para testes)."""
        new_base = Path(path).resolve()

        cls.BASE_DIR = new_base
        cls.EXERGAME_DIR = new_base / "exergames"

        for dir_name in cls._get_dir_names():
            if dir_name in ("BASE_DIR", "EXERGAME_DIR"):
                continue
            subdir = dir_name.replace("_DIR", "").lower()
            setattr(cls, dir_name, new_base / subdir)

    # ===================================================================
    # Verificações
    # ===================================================================
    @classmethod
    def config_file_exists(cls, filename: str = CONFIG_FILENAME) -> bool:
        return Path(cls.config(filename)).exists()

    @classmethod
    def calibration_file_exists(
        cls, filename: str = CALIBRATION_FILENAME
    ) -> bool:
        return Path(cls.calibration(filename)).exists()

    # ===================================================================
    # Utilitários
    # ===================================================================
    @classmethod
    def path_help_pt(cls, filename: str) -> str:
        return cls.help(f"pt/{filename}")
