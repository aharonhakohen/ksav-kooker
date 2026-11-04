# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/afink/TorahNotesOCR/main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/afink/TorahNotesOCR/version.json', '.'), ('C:/Users/afink/TorahNotesOCR/model_assets', 'model_assets'), ('C:/Users/afink/TorahNotesOCR/assets', 'assets')],
    hiddenimports=['PyQt6', 'torch', 'PIL', 'docx', 'core.hebocr.recognize', 'core.hebocr.wordlm', 'core.hebocr.lm'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KsavKooker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:/Users/afink/TorahNotesOCR/assets/ksav_kooker.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KsavKooker',
)
