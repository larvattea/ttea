#!/usr/bin/env bash
# Compila o T-TEA para Windows 64 bits a partir do WSL, usando o Python do
# Windows via interoperabilidade (PyInstaller não faz cross-compile de Linux).
#
# Alvo: Windows 7 SP1 / 10 / 11, apenas 64 bits.
#   - Python 3.8.10  -> último Python com suporte a Windows 7
#   - PyInstaller 5.13.2 -> último com bootloader testado em Windows 7
#   - 32 bits é inviável: o MediaPipe nunca publicou wheels win32.
#
# Uso:  ./build_windows.sh
# Saída: C:\Temp\ttea-build\app\Source\dist\T-TEA  (pasta pronta para copiar)
#        C:\Temp\ttea-build\T-TEA-win64.zip
set -euo pipefail

BUILD=/mnt/c/Temp/ttea-build
PROJ="$(cd "$(dirname "$0")" && pwd)"
PY="$BUILD/py38full/python.exe"

mkdir -p "$BUILD"

# 1. Python 3.8.10 do Windows (instalação por usuário, silenciosa, com tkinter).
#    Atenção: o pacote NuGet de Python NÃO serve — vem sem tkinter/Tcl.
if [ ! -f "$PY" ]; then
    curl -L -o "$BUILD/python-3.8.10-amd64.exe" \
        https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
    (cd "$BUILD" && cmd.exe /c "python-3.8.10-amd64.exe /quiet InstallAllUsers=0 \
        PrependPath=0 Include_launcher=0 Include_test=0 AssociateFiles=0 \
        Shortcuts=0 TargetDir=C:\\Temp\\ttea-build\\py38full")
fi

# 2. Copia o projeto para o NTFS (sem artefatos :Zone.Identifier do WSL).
rsync -a --delete --exclude='*Zone.Identifier' --exclude='__pycache__' \
    --exclude='.idea' --exclude='.vs' --exclude='.vscode' \
    --exclude='Source/build' --exclude='Source/dist' \
    "$PROJ/" "$BUILD/app/"

# 3. Dependências (pyobject saiu do PyPI e não é usado pelo código).
# Importante: o WSL não traduz argumentos para .exe do Windows, então o pip
# deve rodar com cwd em C:\ e receber caminhos relativos.
grep -v '^pyobject' "$PROJ/requisitos.txt" > "$BUILD/requisitos-build.txt"
(cd "$BUILD" && "$PY" -m pip install --upgrade pip --quiet --no-warn-script-location)
(cd "$BUILD" && "$PY" -m pip install -r requisitos-build.txt "pyinstaller==5.13.2" \
    --no-warn-script-location --timeout 60 --retries 10)

# 4. Compila (onedir; o jogo lê tudo por caminho relativo ao diretório do exe).
(cd "$BUILD/app/Source" && "$PY" -m PyInstaller T-TEA.spec --noconfirm)

# 5. Junta as pastas de dados ao lado do exe.
DIST="$BUILD/app/Source/dist/T-TEA"
(cd "$BUILD/app/Source" && \
    cp -r Assets Jogadores "Kartea Fases" calibracao.csv "$DIST/" && \
    mkdir -p "$DIST/VesTEA" && \
    cp -r VesTEA/config VesTEA/images VesTEA/labirintos "$DIST/VesTEA/" && \
    cp LEIA-ME.txt "$DIST/")

# 6. Zip final.
(cd "$BUILD/app/Source/dist" && powershell.exe -NoProfile -Command \
    "Compress-Archive -Path 'T-TEA' -DestinationPath 'C:\\Temp\\ttea-build\\T-TEA-win64.zip' -Force")

echo "OK: pasta $DIST"
echo "OK: zip   C:\\Temp\\ttea-build\\T-TEA-win64.zip"
