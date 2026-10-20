# Ajuda da Plataforma T-TEA

Ajuda do usuário em português, inglês e espanhol, aberta pelo menu
**Ajuda** ou pela tecla **F1** em qualquer tela. O conteúdo é escrito em
português (reStructuredText) e compilado com Sphinx em um arquivo
`.qch` por idioma.

## Estrutura

```
resources/help/
├── buildhelp.mk / buildhelp.py   build: pot, po, qch, all, clean
├── capturescreens.py             screenshots das telas nos 3 idiomas
├── source/                       páginas em pt_BR (.rst) + conf.py
│   ├── _static/ajuda.css
│   └── img/                      imagens (nome.png, nome.en_US.png, nome.es_ES.png)
├── locale/en_US/LC_MESSAGES/     traduções (.po), uma por página
├── locale/es_ES/LC_MESSAGES/
└── ttea_pt_BR.qch, ttea_en_US.qch, ttea_es_ES.qch   (gerados, distribuídos)
```

## Preparar o ambiente (uma vez)

```powershell
uv sync --group docs
```

O `qhelpgenerator` vem com o Qt. Se o build não o encontrar, indique o
caminho:

```powershell
$env:QHELPGENERATOR = "C:\Qt\6.8.2\mingw_64\bin\qhelpgenerator.exe"
```

## Gerar a ajuda

Na pasta `resources/help`:

```powershell
uv run make -f buildhelp.mk all     # atualiza os .po e gera os 3 .qch
uv run make -f buildhelp.mk qch     # só gera os .qch
```

Sem `make`: `uv run python buildhelp.py all`.

Depois rode `uv run tests`: o teste confere se toda página usada pelo
F1 existe nos 3 idiomas.

## Fluxo de trabalho

1. **Escrever** em `source/` (português).
2. `make -f buildhelp.mk po` atualiza os `.po`. Frases novas ficam sem
   tradução e as alteradas ficam marcadas como *fuzzy*.
3. **Traduzir** os `.po` de `locale/en_US` e `locale/es_ES` (Poedit ou
   outro editor de `.po`). Frase sem tradução aparece em português.
4. `make -f buildhelp.mk qch` gera os `.qch`.
5. Fazer commit das fontes, dos `.po` e dos `.qch`.

## Imagens

- Imagem igual em todos os idiomas (foto, tela sem texto):
  `img/secao/nome.png`.
- Imagem com texto: crie também `nome.en_US.png` e `nome.es_ES.png`. O
  build de cada idioma usa a versão dele automaticamente.
- Telas da plataforma: `uv run python resources/help/capturescreens.py`
  gera `img/ui/...` nos 3 idiomas. Por padrão usa uma pasta de dados
  vazia, para nenhum dado real aparecer na ajuda; use `--data` com uma
  pasta de dados fictícios.

## F1: qual página abre em cada tela

O mapa fica em `src/ttea/service/helpservice.py`:

- `TOPICS`: id do tópico → página (`cadastro_jogador` →
  `cadastro/jogador.html`).
- `VIEW_TOPICS`: classe da tela → id do tópico (`PlayerListView` →
  `cadastro_jogador`).

Para dar ajuda própria a uma aba ou campo:
`widget.setProperty("help_id", "calibracao")`.

Ao renomear ou mover uma página, atualize `TOPICS`: o teste falha se
alguma página do mapa não existir.
