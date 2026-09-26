<h1>T-TEA</h1>

<div>
  <img
    src="https://user-images.githubusercontent.com/30929090/135135105-c4e4365d-09c5-4398-bc90-e53cc29ec4a9.PNG"
    alt="Estrutura física do T-TEA"
    width="16%"
    align="left"
  >

  <h3>Console para Exergames de Chão Interativo</h3>

  <p align="justify">
    Software para um console de Chão Interativo desenvolvido inicialmente com
    foco no público com Transtorno do Espectro Autista (TEA). O projeto foi
    desenvolvido pelo doutorando André Bonetto Trindade e Gabriel Brunelli
    Pereira, sob orientação do Prof. Marcelo da Silva Hounsell (UDESC). O
    projeto Torre para crianças com Transtorno do Espectro Autista (T-TEA) tem
    como objetivo auxiliar na terapia do processamento sensorial por meio de uma
    plataforma interativa, móvel e de baixo custo.
  </p>

  <p align="justify">
    O hardware é composto por projetor de vídeo, câmera webcam e computador
    convencionais, instalados em uma estrutura física de montagem simples e de
    fácil portabilidade. Reutilizando equipamentos já disponíveis nas
    instituições, o custo final da plataforma é significativamente reduzido.
  </p>
</div>

<br clear="all">

<h2>Jogos</h2>

<p align="justify">
  O jogador controla os jogos com o próprio corpo: a webcam acompanha a posição
  dos pés sobre a área projetada no chão.
</p>

- **KarTEA**: o jogador controla um carro numa estrada com 3 pistas,
  movimentando-se lateralmente para capturar alvos (estrelas) e desviar de
  obstáculos (barreiras). Estimula concentração, atenção, coordenação motora e
  lateralidade.
- **RepeTEA**: jogo de memória em que o jogador repete a sequência de figuras
  apresentada, pisando sobre elas.
- **VesTEA**: o jogador percorre labirintos para vestir o personagem com as
  roupas pedidas.

## Instalação

### Requisitos

- Windows 10 ou 11, 64 bits.
- Webcam e projetor (ou um segundo monitor).

### Instalar

1. Conecte a webcam.
2. Execute o `T-TEA-<versão>-setup.exe` e siga o assistente. Não é preciso ser
   administrador.
3. Se aparecer "O Windows protegeu o computador", clique em **Mais
   informações** → **Executar assim mesmo**. O aviso aparece porque o
   instalador não tem assinatura digital.

O T-TEA é instalado em `%LOCALAPPDATA%\Programs\T-TEA`. Os dados ficam na mesma
pasta e **são mantidos ao atualizar ou desinstalar**:

| Arquivo / pasta | Conteúdo |
|---|---|
| `Jogadores\` | Cadastros e histórico das sessões |
| `calibracao.csv` | Calibração da área projetada |
| `config.json` | Câmera, monitor e inversão de eixos |
| `debug.txt`, `log.txt` | Registros para diagnóstico (até 2 MB cada) |

## Uso

### Configurações

Na engrenagem (⚙) do menu:

- **Câmera**: com prévia ao vivo e o esqueleto detectado desenhado por cima.
- **Monitor** onde os jogos abrem em tela cheia.
- **Projeção invertida na horizontal / vertical**: inverte o eixo
  correspondente do rastreamento dos pés, conforme a montagem do projetor
  (na torre padrão, a projeção é invertida na vertical).

### Calibração

Obrigatória na primeira vez e sempre que a câmera ou o projetor mudarem de
lugar. Sem calibração, os jogos usam a imagem inteira da câmera, sem
alinhamento com a projeção.

- **Calibrar Automaticamente** (recomendado): projeta um tabuleiro e detecta
  os cantos sozinho.
- **Calibrar Manualmente**: clique, na janela da câmera, nos cantos
  **numerados 1, 2, 3 e 4 como aparecem na projeção**.

### Jogar

Escolha o jogador e o jogo no menu. Para sair de um jogo, pressione **Q** ou
use **Parar de Jogar** no menu. Se algo der errado, envie o `debug.txt` para a
equipe do projeto.

## Desenvolvimento

### Requisitos

- Windows 10 ou 11, 64 bits.
- [uv](https://docs.astral.sh/uv/) (recomendado) ou Python 3.10 (64 bits).

### Executar com uv

O uv baixa o Python correto, cria o `.venv` e sincroniza as dependências
sozinho.

```powershell
winget install --id=astral-sh.uv -e
uv run main.py
```

### Executar sem uv (venv manual)

Com o [Python 3.10](https://www.python.org/downloads/windows/) (64 bits)
instalado:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

### Dependências

As versões ficam em `pyproject.toml` e `uv.lock`. O `requirements.txt` é gerado
a partir do `uv.lock`, para quem usa o venv manual. Depois de alterar uma
dependência, atualize os dois:

```powershell
uv lock
uv export --format requirements.txt --no-hashes --no-header --no-annotate --all-groups --no-emit-project -o requirements.txt
```

### Gerar o instalador

Requer o [Inno Setup 6](https://jrsoftware.org/isinfo.php):

```powershell
winget install --id=JRSoftware.InnoSetup -e
powershell -ExecutionPolicy Bypass -File build.ps1
```

Funciona com uv ou com o venv manual. O resultado fica em `build\`:

- `build\T-TEA-<versão>-setup.exe`: instalador.
- `build\dist\T-TEA\`: programa pronto, sem instalador.

Use `-SemInstalador` para gerar só a pasta do programa, sem o Inno Setup. Os
logs de cada etapa ficam em `build\logs\`. A versão vem do `pyproject.toml`.

<br clear="all">

<h1 align="center">Realização</h1>
<p align="center">
  <a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/cd3acfdc-6d5a-45cf-a2aa-5259c1be0cb7" /></a><a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/9b388bc5-bc1f-467a-a674-0ee4a239b9d4" /></a><a href="https://github.com/larvattea"><img height="100" hspace="10" alt="image" src="https://github.com/user-attachments/assets/e4517a7b-de3e-4c8d-baf9-2ea0326aa1e4" /></a>
</p>
