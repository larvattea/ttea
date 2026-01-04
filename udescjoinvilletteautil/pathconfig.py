import os
import sys
from pathlib import Path
from typing import List


class PathConfig:
    """
    Central de caminhos do aplicativo.
    Separa claramente:
      • Recursos embutidos (imagens, .ui, .qm) -> :/ (Qt Resource System)
      • Dados do usuário (logs, jogadores, configs) -> pasta appdata
    """

    # ===================================================================
    # 1. PASTA DE DADOS DO USUÁRIO (escrita permitida)
    # ===================================================================
    # Nome do app
    APP_NAME = "ttea"  # Nome do app

    # Nome do arquivo principal de configuração
    CONFIG_FILENAME = "config.ini"

    if sys.platform.startswith("win"):
        APPDATA_DIR = Path(os.getenv("APPDATA")) / APP_NAME
    elif sys.platform == "darwin":  # macOS
        APPDATA_DIR = (
            Path.home() / "Library" / "Application Support" / APP_NAME
        )
    else:  # Linux e outros
        APPDATA_DIR = Path.home() / ".local" / "share" / APP_NAME

    LOG_DIR = APPDATA_DIR / "log"
    PLAYERS_DIR = APPDATA_DIR / "players"
    GAMES_DIR = (
        APPDATA_DIR / "udescjoinvilletteagames"
    )  # <- jogos da aplicação
    CONFIG_DIR = APPDATA_DIR / "config"
    EXPORTS_DIR = APPDATA_DIR / "exports"  # CSV, relatórios, etc.

    # ===================================================================
    # 2. PASTA RAIZ DO PROJETO (apenas para desenvolvimento)
    # ===================================================================
    if getattr(sys, "frozen", False):
        # App empacotado (PyInstaller)
        PROJECT_ROOT = Path(sys.executable).parent
    else:
        PROJECT_ROOT = Path(__file__).parent.parent.parent

    RESOURCES_DIR = PROJECT_ROOT / "resources"

    # ===================================================================
    # 3. MÉTODOS DE RECURSOS EMBUTIDOS (usam :/ -> funcionam no .exe)
    # ===================================================================
    @staticmethod
    def resource(path: str = "") -> str:
        """Retorna caminho Qt Resource (funciona no .exe)"""
        return f":/{path}".rstrip("/")

    @staticmethod
    def icon_system(name: str) -> str:
        return f":/icons/system/{name}"

    @staticmethod
    def icon_ui(name: str) -> str:
        return f":/icons/ui/{name}"

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
    def help(path: str = "") -> str:
        return f":/help/{path}".rstrip("/")

    # ===================================================================
    # 4. MÉTODOS DE DADOS DO USUÁRIO (escrita)
    # ===================================================================
    @classmethod
    def ensure_user_dirs(cls) -> None:
        """Cria todas as pastas de dados do usuário na primeira execução"""
        for directory in [
            cls.APPDATA_DIR,
            cls.LOG_DIR,
            cls.PLAYERS_DIR,
            cls.GAMES_DIR,
            cls.CONFIG_DIR,
            cls.EXPORTS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def log(cls, filename: str) -> str:
        cls.ensure_user_dirs()
        return str(cls.LOG_DIR / filename)

    @classmethod
    def player(cls, filename: str) -> str:
        cls.ensure_user_dirs()
        return str(cls.PLAYERS_DIR / filename)

    @classmethod
    def game_save(cls, game_name: str, filename: str) -> str:
        cls.ensure_user_dirs()
        game_dir = cls.GAMES_DIR / game_name
        game_dir.mkdir(exist_ok=True)
        return str(game_dir / filename)

    @classmethod
    def export(cls, filename: str) -> str:
        cls.ensure_user_dirs()
        return str(cls.EXPORTS_DIR / filename)

    @classmethod
    def config(cls, filename: str = CONFIG_FILENAME) -> str:
        cls.ensure_user_dirs()
        return str(cls.CONFIG_DIR / filename)

    @classmethod
    def config_file_exists(cls, filename: str = CONFIG_FILENAME) -> bool:
        """Verifica se o arquivo de configuração existe no diretório do usuário.

        Returns
        -------
        bool
            True se o arquivo config.ini existir, False caso contrário.
        """
        cls.ensure_user_dirs()  # Garante que as pastas existam (não cria o arquivo)
        config_path = Path(cls.config(filename))
        return config_path.exists()

    # ===================================================================
    # 5. MÉTODOS LEGADOS (mantidos para compatibilidade)
    # ===================================================================
    @classmethod
    def path_games(cls) -> List[str]:
        """Lista jogos salvos pelo usuário (não mais usado agora)"""
        cls.ensure_user_dirs()
        return [
            d.name
            for d in cls.GAMES_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

    @classmethod
    def path_help_pt(cls, filename: str) -> str:
        return cls.help(f"pt/{filename}")
