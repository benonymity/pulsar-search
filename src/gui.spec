# -*- mode: python ; coding: utf-8 -*-

import os
import sys
# import pkg_resources.py2_warn

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['numpy.random.common', 'numpy.random.bounded_integers', 'numpy.random.entropy', 'pkg_resources.py2_warn', 'dependency_injector.errors'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

if sys.platform == "win32":
    os.system("pip3 install win32clipboard")
    splash = Splash(
        'splash.png',
        binaries=a.binaries,
        datas=a.datas,
        text_pos=(10, 30),
        text_size=12,
        text_color='white',
        minify_script=True,
        always_on_top=True,
    )

    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        splash,
        splash.binaries,
        [],
        name='Pulsar Search.exe',
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
        icon=['icon.icns'],
    )

elif sys.platform == "linux" or sys.platform == "linux2":
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='Pulsar Search',
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
        icon=['icon.icns'],
    )

    os.system("chmod +x dist/pulsar_search")

elif sys.platform == "darwin":
    os.system("pip3 install pasteboard")
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name='pulsar_search',
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
        icon=['icon.icns'],
    )

    os.system("chmod +x dist/pulsar_search")
    app = BUNDLE(
        exe,
        name='Pulsar Search.app',
        icon='icon.icns',
        bundle_identifier=None,
    )

    os.system("chmod +x dist/Pulsar Search.app/Contents/MacOS/pulsar_search")
    os.remove("dist/pulsar_search")