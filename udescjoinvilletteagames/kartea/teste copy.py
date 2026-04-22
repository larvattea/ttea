import numpy as np

# Tenta alocar 100MB de uma vez
try:
    teste = np.zeros((1024, 1024, 25), dtype="float32")
    print("Alocação de 100MB funcionou!")
except Exception as e:
    print(f"Erro na alocação de teste: {e}")
