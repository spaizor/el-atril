# -*- mode: python ; coding: utf-8 -*-
# Compila El Atril en un solo .exe sin consola:
#     .venv\Scripts\pyinstaller build.spec
# Deja "dist\El Atril.exe".
from PyInstaller.utils.hooks import collect_all

# La pagina (HTML, CSS y JS) va dentro del .exe, en la misma ruta que tiene junto al paquete.
datas = [('el_atril/web', 'el_atril/web')]
binaries = []
hiddenimports = ['mistune']

# pywebview trae ficheros propios (JS, DLL de WebView2) que hay que copiar enteros.
d, b, h = collect_all('webview')
datas += d
binaries += b
hiddenimports += h

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='El Atril',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # Sin UPX: los .exe comprimidos con UPX dan mas falsos positivos en los antivirus.
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
