# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['diamond_applicationv2.py'],
    pathex=[],
    binaries=[],
    datas=[('random_forest_model.pkl', '.'), ('train.csv', '.'), ('data_for_scaler.csv', '.'), ('diamond_background.jpg', '.'),
        ('window_icon.png', '.'), ('result_window_icon.png', '.'), ('app_icon.ico', '.')],
    hiddenimports=['sklearn', 'sklearn.ensemble', 'sklearn.tree', 'sklearn.utils._typedefs'],
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
    a.binaries,
    a.datas,
    [],
    name='diamond_applicationv2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)
