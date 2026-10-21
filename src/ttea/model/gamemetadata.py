"""Model for game metadata read from each game's metadata.json.

This module provides the GameMetadata class, which loads and validates the
metadata file (schema 1.x) of a game, or the manifest of a ``.ttea``
cartridge, and exposes the data needed by the platform to list, configure
and launch the game.
"""

import json
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

from .language import Language


@dataclass
class GameMetadata:
    """Metadados de um jogo lidos do metadata.json (schema 1.x).

    Attributes
    ----------
    id : str
        Identificador único do jogo (ex.: "br.udesc.larva.kartea").
    version : str
        Versão do jogo.
    folder_path : Path
        Pasta onde o jogo está instalado.
    entrypoint : str
        Arquivo executado para iniciar o jogo, relativo à pasta do jogo.
    view_factory : Optional[str]
        Caminho completo da classe de fábrica de views do jogo.
    menu_actions : Dict[str, dict]
        Ações que o jogo adiciona ao menu de configurações da plataforma.
    icon : Optional[str]
        Caminho do ícone, relativo à pasta do jogo.
    developers : List[str]
        Nomes dos desenvolvedores.
    release_date : Optional[str]
        Data de lançamento (ISO ou apenas o ano).
    required_peripherals : List[str]
        Periféricos necessários (ex.: "webcam", "projector").
    localization : Dict[str, Dict[str, str]]
        Textos por idioma (name, short_description, about_the_game...).
    default_language : str
        Idioma usado quando o idioma da plataforma não estiver disponível.
    raw : Dict[str, Any]
        Conteúdo completo do JSON, para campos ainda não mapeados.
    """

    SUPPORTED_SCHEMA_MAJOR: ClassVar[str] = "1"
    FILENAME: ClassVar[str] = "metadata.json"
    CARTRIDGE_EXTENSION: ClassVar[str] = ".ttea"
    CARTRIDGE_MANIFEST: ClassVar[str] = "manifest.json"

    id: str
    version: str
    folder_path: Path
    entrypoint: str
    view_factory: Optional[str]
    menu_actions: Dict[str, dict]
    icon: Optional[str]
    developers: List[str]
    release_date: Optional[str]
    required_peripherals: List[str]
    localization: Dict[str, Dict[str, str]]
    default_language: str
    raw: Dict[str, Any] = field(repr=False, default_factory=dict)

    # ---------- leitura ----------
    @classmethod
    def load(cls, path: Path) -> "GameMetadata":
        """Lê o metadata.json e devolve um GameMetadata.

        Parameters
        ----------
        path : Path
            Caminho do arquivo metadata.json.

        Returns
        -------
        GameMetadata
            Metadados do jogo.

        Raises
        ------
        ValueError
            Se o JSON for inválido, o schema não for suportado ou faltar
            um campo obrigatório.
        """
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        schema = str(data.get("schema_version", ""))
        if schema.split(".")[0] != cls.SUPPORTED_SCHEMA_MAJOR:
            raise ValueError(
                f"{path}: schema_version '{schema}' não suportado "
                f"(esperado {cls.SUPPORTED_SCHEMA_MAJOR}.x)"
            )

        try:
            return cls._parse(data, path.parent)
        except KeyError as e:
            raise ValueError(
                f"{path}: campo obrigatório ausente: {e}"
            ) from e

    @classmethod
    def _parse(cls, d: dict, folder: Path) -> "GameMetadata":
        runtime = d["runtime"]
        store = d.get("store", {})
        loc = store.get("localization", {})

        return cls(
            id=d["id"],
            version=d["version"],
            folder_path=folder,
            entrypoint=runtime["entrypoint"],
            view_factory=runtime.get("view_factory"),
            menu_actions=runtime.get("menu_actions") or {},
            icon=(store.get("assets") or {}).get("icon"),
            developers=[
                dev["name"] for dev in store.get("developers") or []
            ],
            release_date=(store.get("release_date") or {}).get("date"),
            required_peripherals=runtime.get("required_peripherals") or [],
            localization={
                k: v for k, v in loc.items() if isinstance(v, dict)
            },
            default_language=loc.get("default", "en_US"),
            raw=d,
        )

    @classmethod
    def load_cartridge(cls, path: Path) -> "GameMetadata":
        """Lê o manifest.json de um cartucho .ttea e devolve um GameMetadata.

        O cartucho é executado pelo comando externo ``tsdk``; aqui só são
        lidos os dados exibidos na tela de sessão de jogo.

        Parameters
        ----------
        path : Path
            Caminho do arquivo .ttea.

        Returns
        -------
        GameMetadata
            Metadados do jogo, com ``entrypoint`` igual ao nome do arquivo.

        Raises
        ------
        ValueError
            Se o arquivo não for um cartucho válido ou faltar um campo
            obrigatório no manifest.json.
        """
        path = Path(path)
        try:
            with zipfile.ZipFile(path) as zf:
                data = json.loads(zf.read(cls.CARTRIDGE_MANIFEST))
        except (
            zipfile.BadZipFile,
            zlib.error,
            EOFError,
            KeyError,
            ValueError,
            NotImplementedError,
            RuntimeError,
            OSError,
        ) as e:
            raise ValueError(f"{path}: cartucho inválido: {e}") from e
        if not isinstance(data, dict):
            raise ValueError(f"{path}: manifest.json deve ser um objeto")

        for key in ("id", "version"):
            if not isinstance(data.get(key), str) or not data[key]:
                raise ValueError(f"{path}: campo obrigatório ausente: '{key}'")

        localization: Dict[str, Dict[str, str]] = {}
        for manifest_key, key in (
            ("name", "name"),
            ("description", "short_description"),
        ):
            if manifest_key == "description" and manifest_key not in data:
                continue
            texts = cls._cartridge_texts(data.get(manifest_key))
            if texts is None:
                raise ValueError(
                    f"{path}: '{manifest_key}' deve ser um texto ou um "
                    f"mapa de idioma para texto"
                )
            for code, value in texts.items():
                localization.setdefault(code, {})[key] = value

        default_language = (
            "en_US" if "en_US" in localization else next(iter(localization))
        )
        return cls(
            id=data["id"],
            version=data["version"],
            folder_path=path.parent,
            entrypoint=path.name,
            view_factory=None,
            menu_actions={},
            icon=None,
            developers=[],
            release_date=None,
            required_peripherals=[],
            localization=localization,
            default_language=default_language,
            raw=data,
        )

    @staticmethod
    def _cartridge_texts(value: Any) -> Optional[Dict[str, str]]:
        """Converte name/description do manifest em textos por idioma.

        Um texto simples vale para o idioma padrão ("en_US"). Num mapa, as
        tags BCP 47 ("pt-BR", "es") viram os códigos da plataforma
        ("pt_BR", "es_ES"); a tag exata prevalece sobre o prefixo.
        """
        if isinstance(value, str) and value.strip():
            return {"en_US": value}
        if not isinstance(value, dict) or not value:
            return None

        codes = [lang["code"] for lang in Language.LANGUAGES]
        exact: Dict[str, str] = {}
        by_prefix: Dict[str, str] = {}
        for tag, text in value.items():
            if not isinstance(tag, str) or not isinstance(text, str):
                return None
            if not text.strip():
                return None
            tag = tag.replace("-", "_")
            match = next((c for c in codes if c.lower() == tag.lower()), None)
            if match:
                exact[match] = text
                continue
            prefix = tag.split("_")[0].lower()
            match = next(
                (c for c in codes if c.lower().startswith(prefix + "_")), tag
            )
            by_prefix.setdefault(match, text)
        return {**by_prefix, **exact}

    # ---------- acesso ----------
    def text(self, lang: str, key: str, default: str = "") -> str:
        """Texto no idioma pedido, com fallback para o idioma padrão do jogo."""
        for code in (lang, self.default_language):
            value = self.localization.get(code, {}).get(key)
            if value:
                return value
        return default

    def name(self, lang: str) -> str:
        """Nome de exibição do jogo no idioma pedido."""
        return self.text(lang, "name", self.id)

    @property
    def icon_path(self) -> str:
        """Caminho absoluto do ícone, ou string vazia."""
        return str(self.folder_path / self.icon) if self.icon else ""

    @property
    def entrypoint_path(self) -> Path:
        """Caminho absoluto do arquivo que inicia o jogo."""
        return self.folder_path / self.entrypoint

    @property
    def release_year(self) -> str:
        """Ano de lançamento (primeiros 4 caracteres da data)."""
        return (self.release_date or "")[:4]
