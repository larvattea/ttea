"""Inicia o T-TEA a partir da raiz do projeto: `uv run main.py` ou `python main.py`."""
import os
import runpy
import sys

# Os jogos leem e gravam tudo (Assets, Jogadores, calibracao.csv...) por
# caminho relativo a pasta Source, entao roda o menu de dentro dela.
source = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Source')
os.chdir(source)
sys.path.insert(0, source)
runpy.run_path(os.path.join(source, 'TTEA_menu.py'), run_name='__main__')
