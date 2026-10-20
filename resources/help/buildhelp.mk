# ==============================================================
# buildhelp.mk – Ajuda da Plataforma T-TEA (pt_BR, en_US, es_ES)
# Works on Windows + Linux + macOS. The logic is in buildhelp.py.
# ==============================================================

PYTHON ?= python

.DEFAULT_GOAL := help

all pot po qch clean:
	@$(PYTHON) buildhelp.py $@

help:
	@echo "Available commands:"
	@echo "  all    -> update the .po catalogs and build the 3 .qch files"
	@echo "  pot    -> extract the texts of the pages (pt_BR)"
	@echo "  po     -> update locale/en_US and locale/es_ES (.po)"
	@echo "  qch    -> build ttea_pt_BR.qch, ttea_en_US.qch, ttea_es_ES.qch"
	@echo "  clean  -> remove _build/"

.PHONY: all pot po qch clean help

# ==============================================================
# Usage (from resources/help, after: uv sync --group docs)
# ==============================================================
#
#   uv run make -f buildhelp.mk all
#   uv run make -f buildhelp.mk qch
#
# Without make:
#   uv run python buildhelp.py all
#
# If qhelpgenerator is not found, point to it, e.g. in PowerShell:
#   $env:QHELPGENERATOR = "C:\Qt\6.8.2\mingw_64\bin\qhelpgenerator.exe"
