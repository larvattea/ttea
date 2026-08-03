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
# Troca opencv-contrib-python por opencv-python: o jogo não usa nenhum modulo
# contrib (checado via grep), e a versão "contrib" carrega ~35 MB de DLL de
# ffmpeg/módulos extras que só incham o pacote final sem uso.
# Importante: o WSL não traduz argumentos para .exe do Windows, então o pip
# deve rodar com cwd em C:\ e receber caminhos relativos.
sed -e '/^pyobject/d' -e 's/^opencv-contrib-python==/opencv-python==/' \
    "$PROJ/requisitos.txt" > "$BUILD/requisitos-build.txt"
(cd "$BUILD" && "$PY" -m pip install --upgrade pip --quiet --no-warn-script-location)
# opencv-contrib-python e opencv-python instalam os mesmos arquivos em cv2/;
# ter os dois instalados ao mesmo tempo corrompe o pacote.
(cd "$BUILD" && "$PY" -m pip uninstall -y opencv-contrib-python --quiet 2>/dev/null || true)
(cd "$BUILD" && "$PY" -m pip install -r requisitos-build.txt "pyinstaller==5.13.2" \
    --no-warn-script-location --timeout 60 --retries 10)

# 4. Compila (onedir; o jogo lê tudo por caminho relativo ao diretório do exe).
(cd "$BUILD/app/Source" && "$PY" -m PyInstaller T-TEA.spec --noconfirm)

# 5. Junta as pastas de dados ao lado do exe.
#    Assets/Repetea_Figuras tem um .pptx de anotações (+ arquivo temporário do
#    Office) que não é lido pelo jogo - fica de fora do pacote distribuído.
DIST="$BUILD/app/Source/dist/T-TEA"
(cd "$BUILD/app/Source" && \
    rsync -a --exclude='*.pptx' --exclude='~$*' Assets "$DIST/" && \
    cp -r Jogadores "Kartea Fases" calibracao.csv "$DIST/" && \
    mkdir -p "$DIST/VesTEA" && \
    cp -r VesTEA/config VesTEA/images VesTEA/labirintos "$DIST/VesTEA/" && \
    cp LEIA-ME.txt "$DIST/")

# 6. Zip final. Compress-Archive já usa o nível "Optimal" do Deflate (o
#    Windows PowerShell 5.1 nem expõe um nível mais forte que esse); o ganho
#    real de tamanho vem de reduzir o conteúdo, não de trocar o algoritmo -
#    um formato mais forte (7z/xz) quebraria a extração nativa no Windows 7.
rm -f /mnt/c/Temp/ttea-build/T-TEA-win64.zip
(cd "$BUILD/app/Source/dist" && powershell.exe -NoProfile -Command \
    "Compress-Archive -Path 'T-TEA' -DestinationPath 'C:\\Temp\\ttea-build\\T-TEA-win64.zip' -Force")

echo "OK: pasta $DIST"
echo "OK: zip   C:\\Temp\\ttea-build\\T-TEA-win64.zip"
