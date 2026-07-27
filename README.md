# Torre para crianças com Transtorno do Espectro Autista (T-TEA)
Um sistema do Chão Interativo que está sendo desenvolvido pelo mestrando André Bonetto Trindade e Gabriel Brunelli Pereira, orientado pelo Prof. Marcelo da Silva Hounsell (UDESC), o projeto Torre para crianças com Transtorno do Espectro Autista (T-TEA) tem o objetivo de auxiliar na terapia do processamento sensorial de autistas, utilizando uma plataforma interativa de baixo custo e móvel provida de jogos sérios.

O hardware do projeto será composto por projetor de vídeo, câmera webcam e computador convencionais. A webcam é um dispositivo relativamente barato e pode ser encontrado com facilidade, o que pode ser visto como fator positivo para adoção do jogo em instituições públicas. 

Sendo que o projetor e o computador são convencionais, pode-se utilizar os que já se tem dísponíveis nas instituições. Desta forma, reutilizando equipamento, o custo final da plataforma T-TEA é significamente reduzido. 

Estes equipamentos serão instalados em uma estrutura mecânica de montagem simples e de fácil portabilidade. O modelo pode ser visto na Figura abaixo. A área de projeção terá 5,25 metros quadrados, sendo 3 metros de largura por 1,7 metros de altura, estas medidas estão sujeitas a mudanças após testes iniciais.

![hardware](https://user-images.githubusercontent.com/30929090/135135105-c4e4365d-09c5-4398-bc90-e53cc29ec4a9.PNG)

## Desenvolvimento

Requerimentos:
- [uv](https://docs.astral.sh/uv/), que baixa e gerencia automaticamente o Python 3.10 caso ele ainda não esteja instalado.
- Computador com arquitetura x86-64 ou ARM.

### Instalar o uv

macOS:

```bash
brew install uv
```

Windows (PowerShell):

```powershell
winget install --id=astral-sh.uv -e
```

Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Executar

Na raiz do projeto, em qualquer sistema:

```bash
uv run dev
```

Esse comando baixa o Python 3.10, cria o `.venv`, sincroniza as dependências e inicia o T-TEA.

Para usar `python main.py` diretamente, ative antes o ambiente com `source .venv/bin/activate` no macOS/Linux ou `.venv\Scripts\Activate.ps1` no Windows.

No primeiro uso, permita o acesso à câmera nas configurações de privacidade do sistema.
