"""Build the T-TEA user help in Portuguese, English and Spanish.

Targets
-------
pot
    Extract the texts of the pages (source/, pt_BR) into _build/gettext.
po
    Run ``pot`` and update the catalogs in locale/en_US and
    locale/es_ES.
    Translators then edit the .po files (e.g. with Poedit).
qch
    Build ``ttea_<language>.qch`` for every language, next to this file.
all
    ``po`` followed by ``qch``.
clean
    Remove _build/.

Usage
-----
From this folder, with the docs dependencies installed
(``uv sync --group docs``)::

    python buildhelp.py all

Set ``QHELPGENERATOR`` to the full path of ``qhelpgenerator`` if it is
not found automatically.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
LOCALE = HERE / "locale"
BUILD = HERE / "_build"

BASENAME = "ttea"
SOURCE_LANGUAGE = "pt_BR"
TRANSLATIONS = ("en_US", "es_ES")
LANGUAGES = (SOURCE_LANGUAGE, *TRANSLATIONS)

# Title of the help (window title and root of the contents).
TITLES = {
    "pt_BR": "Ajuda da Plataforma T-TEA",
    "en_US": "T-TEA Platform Help",
    "es_ES": "Ayuda de la Plataforma T-TEA",
}


def namespace(language: str) -> str:
    """Return the help namespace of ``language``.

    The namespace is the host part of the help URLs
    (``qthelp://<namespace>/doc/page.html``), so it is lowercase, as
    URLs lowercase hosts, and uses ``-`` instead of ``_``.

    Examples
    --------
    >>> namespace("pt_BR")
    'br.udesc.larva.ttea.pt-br'
    """
    return f"br.udesc.larva.ttea.{language.lower().replace('_', '-')}"


def run(command: list) -> None:
    """Run ``command`` and stop on error."""
    command = [str(part) for part in command]
    print("$", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def sphinx(builder: str, outdir: Path, *options: str) -> None:
    """Run sphinx-build with ``builder`` into ``outdir``."""
    doctrees = BUILD / "doctrees" / outdir.name
    run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            builder,
            "-d",
            doctrees,
            *options,
            SOURCE,
            outdir,
        ]
    )


def find_qhelpgenerator() -> str:
    """Return the path of qhelpgenerator, or exit with instructions."""
    if path := os.environ.get("QHELPGENERATOR"):
        return path

    for name in ("qhelpgenerator", "pyside6-qhelpgenerator"):
        if path := shutil.which(name):
            return path

    exe = "qhelpgenerator.exe" if os.name == "nt" else "qhelpgenerator"
    candidates = []
    try:
        import PySide6  # noqa: PLC0415

        base = Path(PySide6.__file__).parent
        candidates += [
            base / exe,
            base / "Qt" / "libexec" / exe,
            base / "Qt" / "bin" / exe,
        ]
    except ImportError:
        pass
    if os.name == "nt":
        candidates += sorted(
            Path("C:/Qt").glob(f"6.*/*/bin/{exe}"), reverse=True
        )
    else:
        candidates += [Path("/usr/lib/qt6/libexec") / exe]
        candidates += sorted(
            Path.home().glob(f"Qt/6.*/*/libexec/{exe}"), reverse=True
        )

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    sys.exit(
        "qhelpgenerator not found. Install Qt 6 (e.g. C:\\Qt\\6.x\\...\\bin) "
        "or set QHELPGENERATOR to its full path."
    )


# ----------------------------------------------------------------------
# Targets
# ----------------------------------------------------------------------
def target_pot() -> None:
    """Extract the translatable texts of the Portuguese pages."""
    sphinx("gettext", BUILD / "gettext")


def target_po() -> None:
    """Update the en_US and es_ES catalogs with the current texts."""
    target_pot()
    languages = [arg for lang in TRANSLATIONS for arg in ("-l", lang)]
    intl = shutil.which("sphinx-intl")
    command = [intl] if intl else [sys.executable, "-m", "sphinx_intl"]
    run(
        [*command, "update", "-p", BUILD / "gettext", "-d", LOCALE, *languages]
    )


def target_qch() -> None:
    """Build one .qch per language."""
    generator = find_qhelpgenerator()
    for language in LANGUAGES:
        outdir = BUILD / "qthelp" / language
        sphinx(
            "qthelp",
            outdir,
            "-D",
            f"language={language}",
            "-D",
            f"qthelp_namespace={namespace(language)}",
            "-D",
            f"html_title={TITLES[language]}",
        )
        output = HERE / f"{BASENAME}_{language}.qch"
        run([generator, outdir / f"{BASENAME}.qhp", "-o", output])
        print(f"==> {output.name}", flush=True)


def target_all() -> None:
    """Update the catalogs and build every .qch."""
    target_po()
    target_qch()


def target_clean() -> None:
    """Remove the intermediate build folder."""
    shutil.rmtree(BUILD, ignore_errors=True)
    print(f"Removed {BUILD}")


TARGETS = {
    "pot": target_pot,
    "po": target_po,
    "qch": target_qch,
    "all": target_all,
    "clean": target_clean,
}


def main() -> None:
    """Run the targets given on the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="+", choices=TARGETS)
    for name in parser.parse_args().targets:
        TARGETS[name]()


if __name__ == "__main__":
    main()
