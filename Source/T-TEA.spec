# -*- mode: python ; coding: utf-8 -*-
# Build: use build.ps1 na raiz do projeto (roda o PyInstaller a partir de Source/).
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

# mediapipe carries .tflite/.binarypb model files that must be bundled.
# collect_all() grabs the data for every solution (hands, face, iris,
# holistic, objectron, selfie_segmentation...), but the game only ever uses
# mp.solutions.pose (confirmed via grep across the whole codebase). Drop the
# model files for the other solutions - this alone is ~20 MB uncompressed.
mp_datas, mp_binaries, mp_hidden = collect_all('mediapipe')
_MP_SOLUCOES_NAO_USADAS = (
    os.path.join('mediapipe', 'modules', 'face_detection'),
    os.path.join('mediapipe', 'modules', 'face_geometry'),
    os.path.join('mediapipe', 'modules', 'face_landmark'),
    os.path.join('mediapipe', 'modules', 'hand_landmark'),
    os.path.join('mediapipe', 'modules', 'holistic_landmark'),
    os.path.join('mediapipe', 'modules', 'iris_landmark'),
    os.path.join('mediapipe', 'modules', 'objectron'),
    os.path.join('mediapipe', 'modules', 'palm_detection'),
    os.path.join('mediapipe', 'modules', 'selfie_segmentation'),
)
mp_datas = [
    (src, dest) for src, dest in mp_datas
    if not any(alvo in dest for alvo in _MP_SOLUCOES_NAO_USADAS)
]

# Ferramenta de calibração automática (ChArUco), auto_calibracao_espelho.py,
# fica na raiz do projeto (um nível acima de Source/) e é chamada em processo
# pelo botão "Calibração Automática" do menu - não vira um .exe separado
# porque isso duplicaria opencv/numpy (~65 MB) no zip final.
_screeninfo_hidden = collect_submodules('screeninfo')

a = Analysis(
    ['TTEA_menu.py'],
    pathex=['..'],
    binaries=mp_binaries,
    datas=mp_datas,
    hiddenimports=mp_hidden + _screeninfo_hidden + ['auto_calibracao_espelho'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='T-TEA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=os.path.join(SPECPATH, '..', 'installer', 'ttea.ico'),
    # Mantem tudo ao lado do T-TEA.exe (o padrao do PyInstaller 6 e uma
    # subpasta _internal), como nas versoes anteriores do pacote.
    contents_directory='.',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='T-TEA',
)
