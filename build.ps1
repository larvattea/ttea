<#
.SYNOPSIS
    Gera o instalador do T-TEA para Windows (64 bits).

.DESCRIPTION
    1. Prepara o ambiente Python (uv, ou um .venv criado manualmente).
    2. Compila o programa com o PyInstaller (Source\T-TEA.spec).
    3. Junta os recursos dos jogos ao lado do executavel.
    4. Gera o instalador com o Inno Setup (installer\T-TEA.iss).

    Saida:
      build\dist\T-TEA\                programa pronto (pasta)
      build\T-TEA-<versao>-setup.exe   instalador

    Os detalhes de cada etapa vao para build\logs\; o terminal so mostra o
    andamento (e o final do log, se algo falhar).

.PARAMETER SemInstalador
    Para depois de montar build\dist\T-TEA, sem gerar o instalador (nao
    precisa do Inno Setup).

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File build.ps1
#>
param(
    [switch]$SemInstalador
)

$ErrorActionPreference = 'Stop'
$Raiz = $PSScriptRoot
$Build = Join-Path $Raiz 'build'
$Logs = Join-Path $Build 'logs'
$Dist = Join-Path $Build 'dist\T-TEA'

function Etapa($texto) { Write-Host "==> $texto" -ForegroundColor Cyan }

function Falhar($texto, $log) {
    Write-Host "ERRO: $texto" -ForegroundColor Red
    if ($log -and (Test-Path $log)) {
        Write-Host "--- ultimas linhas de $log ---"
        Get-Content $log -Tail 30
    }
    exit 1
}

# Roda um programa externo mandando toda a saida para um log.
function Executar($nome, $exe, [string[]]$argumentos, $pasta = $Raiz) {
    $log = Join-Path $Logs "$nome.log"
    Push-Location $pasta
    try {
        # Programas nativos escrevem avisos no stderr; no Windows PowerShell
        # isso vira erro com ErrorActionPreference=Stop. Vale o codigo de saida.
        $ErrorActionPreference = 'Continue'
        & $exe @argumentos 2>&1 | Out-File -FilePath $log -Encoding utf8
        $codigo = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    if ($codigo -ne 0) { Falhar "$nome falhou (codigo $codigo)." $log }
}

New-Item -ItemType Directory -Force $Logs | Out-Null

$Versao = (Select-String -Path (Join-Path $Raiz 'pyproject.toml') -Pattern '^version\s*=\s*"(.+)"').Matches[0].Groups[1].Value
Write-Host "T-TEA $Versao" -ForegroundColor White

# --- 1. Ambiente Python -------------------------------------------------------
$Python = Join-Path $Raiz '.venv\Scripts\python.exe'
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Etapa 'Sincronizando dependencias (uv)'
    Executar 'uv-sync' 'uv' @('sync', '--all-groups', '--frozen')
} elseif (Test-Path $Python) {
    Etapa 'uv nao encontrado, usando o .venv existente'
} else {
    Falhar ('Nenhum ambiente Python. Instale o uv (winget install --id=astral-sh.uv -e) ' +
            'ou crie o .venv manualmente (veja o README).')
}
Executar 'checar-ambiente' $Python @('-c', 'import PyInstaller, mediapipe, cv2.aruco')

# O pip nao traz o modelo "lite" de pose (model_complexity=0, usado pelos
# jogos): o mediapipe baixa ele na primeira vez que e usado. Forca o download
# aqui para ele ir dentro do instalador - o computador da clinica pode nao ter
# internet.
Etapa 'Baixando o modelo de pose do mediapipe'
Executar 'modelo-pose' $Python @('-c', 'import mediapipe as mp; mp.solutions.pose.Pose(model_complexity=0).close()')

# --- 2. PyInstaller ----------------------------------------------------------
Etapa 'Compilando com o PyInstaller (demora alguns minutos)'
if (Test-Path $Dist) { Remove-Item -Recurse -Force $Dist }
Executar 'pyinstaller' $Python @('-m', 'PyInstaller', 'T-TEA.spec', '--noconfirm',
    '--distpath', (Join-Path $Build 'dist'), '--workpath', (Join-Path $Build 'pyinstaller')) (Join-Path $Raiz 'Source')

# --- 3. Recursos dos jogos ---------------------------------------------------
# Os jogos leem tudo por caminho relativo a pasta do executavel.
Etapa 'Copiando recursos dos jogos'
$Source = Join-Path $Raiz 'Source'
$pastas = @(
    @('Assets', 'Assets'),
    @('Jogadores', 'Jogadores'),
    @('Kartea Fases', 'Kartea Fases'),
    @('VesTEA\config', 'VesTEA\config'),
    @('VesTEA\images', 'VesTEA\images'),
    @('VesTEA\labirintos', 'VesTEA\labirintos')
)
foreach ($p in $pastas) {
    # Assets\Repetea_Figuras tem um .pptx de anotacoes (e temporarios do
    # Office) que os jogos nao usam.
    & robocopy (Join-Path $Source $p[0]) (Join-Path $Dist $p[1]) /E /XF '*.pptx' '~$*' /NFL /NDL /NJH /NJS /NP 2>&1 | Out-File -Append -FilePath (Join-Path $Logs 'recursos.log') -Encoding utf8
    if ($LASTEXITCODE -ge 8) { Falhar "falha ao copiar $($p[0])." (Join-Path $Logs 'recursos.log') }
}
$global:LASTEXITCODE = 0

if (-not (Test-Path (Join-Path $Dist 'mediapipe\modules\pose_landmark\pose_landmark_lite.tflite'))) {
    Falhar 'o modelo pose_landmark_lite.tflite nao foi incluido no programa.'
}
Write-Host "    programa: $Dist"

if ($SemInstalador) { exit 0 }

# --- 4. Instalador (Inno Setup) ----------------------------------------------
$Iscc = (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
if (-not $Iscc) {
    $Iscc = @(
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $Iscc) {
    Falhar ('Inno Setup 6 nao encontrado. Instale com: winget install --id=JRSoftware.InnoSetup -e ' +
            '(ou rode com -SemInstalador para gerar so a pasta do programa).')
}

Etapa 'Gerando o instalador (Inno Setup)'
Executar 'inno-setup' $Iscc @("/DAppVersion=$Versao", "/DAppDir=$Dist", (Join-Path $Raiz 'installer\T-TEA.iss'))
Write-Host "    instalador: $(Join-Path $Build "T-TEA-$Versao-setup.exe")" -ForegroundColor Green
