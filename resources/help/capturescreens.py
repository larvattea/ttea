"""Capture screenshots of the T-TEA screens in every language.

Each screen is opened once per language and saved where the help pages
expect it, following ``figure_language_filename`` in source/conf.py::

    source/img/ui/<name>.png          pt_BR (default)
    source/img/ui/<name>.en_US.png    en_US
    source/img/ui/<name>.es_ES.png    es_ES

Usage
-----
From the project root::

    cd resources/help
    uv run python capturescreens.py                 # all screens
    uv run python capturescreens.py cadastro/jogador_lista
    uv run python capturescreens.py --data C:/dados_exemplo

Notes
-----
By default the screens read an empty, temporary data folder, so no real
player or professional appears in the help. Use ``--data`` to point to
a folder with fictitious example records (same layout as ``data/``).

Screens that open the camera (manual and automatic calibration) are not
captured; take those screenshots by hand.
"""

import argparse
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import QApplication, QWidget

from ttea.factory import AppViewFactory, ViewFactory
from ttea.model import AppModel, Language
from ttea.service import LanguageService
from ttea.util import PathConfig

OUTPUT = Path(__file__).resolve().parent / "source" / "img" / "ui"
KARTEA_ID = "br.udesc.larva.kartea"


def _kartea(method: str) -> Callable[[], QWidget]:
    """Return a creator for a KarTEA screen (game plugin factory)."""

    def create() -> QWidget:
        ViewFactory.discover_games()
        return getattr(ViewFactory.get_game_view_factory(KARTEA_ID), method)()

    return create


# Output name -> function that creates the screen.
_app = AppViewFactory
SCREENS: dict[str, Callable[[], QWidget]] = {
    "introducao/janela_principal": _app.create_main_view,
    "introducao/sobre": _app.create_about_view,
    "cadastro/instituicao_lista": _app.create_institutionfacility_list_view,
    "cadastro/instituicao_edicao": _app.create_institutionfacility_edit_view,
    "cadastro/profissional_lista": _app.create_professional_list_view,
    "cadastro/profissional_edicao": _app.create_professional_edit_view,
    "cadastro/jogador_lista": _app.create_player_list_view,
    "cadastro/jogador_edicao": _app.create_player_edit_view,
    "exergames/sessao_de_jogo": _app.create_playergamelauch_view,
    "configuracoes/calibracao": _app.create_calibration_view,
    "sistema/configuracao_calibracao": _app.create_calibrationsetting_view,
    "sistema/idioma": _app.create_language_view,
    "jogos/kartea/configuracao_lista": _kartea(
        "create_player_config_list_view"
    ),
    "jogos/kartea/configuracao_edicao": _kartea(
        "create_player_config_edit_view"
    ),
}


def output_file(name: str, language: str) -> Path:
    """Return the image path of screen ``name`` in ``language``."""
    suffix = "" if language == Language.DEFAULT_LANGUAGE else f".{language}"
    return OUTPUT / f"{name}{suffix}.png"


def capture(app: QApplication, name: str, language: str) -> None:
    """Open screen ``name``, save its picture and dispose of it."""
    view = SCREENS[name]()
    try:
        view.show()
        for _ in range(10):  # let layouts and late updates settle
            app.processEvents()
        target = output_file(name, language)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not view.grab().save(str(target)):
            raise OSError(f"could not save {target}")
        print(f"  {target.relative_to(OUTPUT.parent)}")
    finally:
        # hide() instead of close(): several screens ask for
        # confirmation when closed.
        view.hide()
        view.deleteLater()
        app.processEvents()


def main() -> int:
    """Capture the requested screens in every language."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "screens", nargs="*", help="screens to capture (default: all)"
    )
    parser.add_argument(
        "--data", type=Path, help="data folder with fictitious example records"
    )
    args = parser.parse_args()
    unknown = sorted(set(args.screens) - set(SCREENS))
    if unknown:
        parser.error(
            f"unknown screens: {', '.join(unknown)}. "
            f"Available: {', '.join(SCREENS)}"
        )
    screens = args.screens or list(SCREENS)

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        PathConfig.set_base_dir(args.data or tmp)
        app = QApplication.instance() or QApplication(sys.argv)
        language_service = LanguageService()
        failures = []

        for language in (lang["code"] for lang in Language.LANGUAGES):
            print(f"[{language}]")
            language_service.preview_language(language)
            AppModel.get_instance().current_language = language
            for name in screens:
                try:
                    capture(app, name, language)
                except Exception as error:  # report and keep going
                    failures.append(f"{language} {name}: {error}")

    for failure in failures:
        print("FAILED", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
