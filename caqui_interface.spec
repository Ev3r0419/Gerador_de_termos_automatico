# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['caqui_interface.py'],
    pathex=[],
    binaries=[],
    datas=[('.\\Modelo de termo VPN.docx', '.'), ('.\\Termo Telecom.docx', '.'), ('.\\Modelo do Termo de Administrador Local.docx', '.'), ('.\\Termo de Responsabilidade de Emprestimo de Equipamento.docx', '.'), ('caqui.ico', '.')],
    hiddenimports=[],
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
    name='Caquimetro',
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
    icon=['caqui.ico'],
)
