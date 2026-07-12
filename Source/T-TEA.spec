# -*- mode: python ; coding: utf-8 -*-
# Build: python -m PyInstaller T-TEA.spec (run from the Source directory)
from PyInstaller.utils.hooks import collect_all

# mediapipe carries .tflite/.binarypb model files that must be bundled
mp_datas, mp_binaries, mp_hidden = collect_all('mediapipe')

a = Analysis(
    ['TTEA_menu.py'],
    pathex=[],
    binaries=mp_binaries,
    datas=mp_datas,
    hiddenimports=mp_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['TTEA_menu_copy', 'RepeTEA copy', 'calibracao copy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
