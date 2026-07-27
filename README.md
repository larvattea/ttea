# Torre para crianças com Transtorno do Espectro Autista (T-TEA)

<img src="resources/images/tteahardware.jpg" alt="Estrutura física do T-TEA" width="20%" align="left">

<p align="justify">Software para um console de Chão Interativo desenvolvido pelo doutorando André Bonetto Trindade e Gabriel Brunelli Pereira, orientado pelo Prof. Marcelo da Silva Hounsell (UDESC), o projeto Torre para crianças com Transtorno do Espectro Autista (T-TEA) tem o objetivo de auxiliar na terapia do processamento sensorial de autistas, utilizando uma plataforma interativa de baixo custo e móvel provida de jogos sérios.</p>
<p align="justify">O hardware é composto por projetor de vídeo, câmera webcam e computador convencionais. A webcam é um dispositivo relativamente barato e pode ser encontrado com facilidade, o que pode ser visto como fator positivo para adoção do jogo em instituições públicas.</p>
<p align="justify">Sendo que o projetor e o computador são convencionais, pode-se utilizar os que já se tem dísponíveis nas instituições. Desta forma, reutilizando equipamento, o custo final da plataforma T-TEA é significamente reduzido.</p>
<p align="justify">Estes equipamentos são instalados em uma estrutura física de montagem simples e de fácil portabilidade.</p>

<br clear="left">

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

No primeiro uso, permita o acesso à câmera nas configurações de privacidade do sistema.
