from pathlib import Path

import chardet
from charset_normalizer import detect as detect_normalizer

base_path = Path(__file__).parent
file_path = base_path / "4_saúde_player.csv"

# Lendo os bytes brutos do arquivo (essencial para detecção)
with open(file_path, "rb") as f:
    raw_data = f.read()

# 1. Usando CHARDET
res_chardet = chardet.detect(raw_data)
print(f"--- CHARDET ---")
print(f"Encoding: {res_chardet['encoding']}")
print(f"Confiança: {res_chardet['confidence']:.2%}\n")

# 2. Usando CHARSET-NORMALIZER
res_normalizer = detect_normalizer(raw_data)
print(f"--- CHARSET-NORMALIZER ---")
print(f"Encoding: {res_normalizer['encoding']}")
print(f"Confiança: {res_normalizer['confidence']:.2%}")
