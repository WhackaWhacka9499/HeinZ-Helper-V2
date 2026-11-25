# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

ROOT_DIR = os.path.abspath(os.path.join(SPECPATH, '..'))

def _collect_clean_tree(src_dir, dst_prefix):
    entries = []
    skip_exts = {'.pyc', '.pyo', '.log', '.xlsx', '.csv'}
    skip_names = {'detected_environment.json', 'bot status.json', 'bot config.json', 'client profiles.json'}
    for dirpath, dirnames, filenames in os.walk(src_dir):
        dirnames[:] = [d for d in dirnames if d != '__pycache__']
        rel = os.path.relpath(dirpath, src_dir)
        target_dir = dst_prefix if rel == '.' else os.path.join(dst_prefix, rel)
        for fn in filenames:
            low = fn.lower()
            if low in skip_names or os.path.splitext(low)[1] in skip_exts:
                continue
            entries.append((os.path.join(dirpath, fn), target_dir))
    return entries


datas = [
    (os.path.join(ROOT_DIR, 'launcher', 'web'), 'web'),
    (os.path.join(ROOT_DIR, 'launcher', 'assets'), 'assets'),
]
datas += _collect_clean_tree(os.path.join(ROOT_DIR, 'tools'), 'tools')
datas += _collect_clean_tree(os.path.join(ROOT_DIR, 'daemon'), 'daemon')
datas += _collect_clean_tree(os.path.join(ROOT_DIR, 'api'), 'api')
binaries = []
hiddenimports = [
    'bottle', 'proxy_tools', 'frida', 'openpyxl', 'psutil', 'requests',
    'sqlite3', '_sqlite3', 'http.server', 'urllib.request', 'urllib.parse',
    'urllib.error', 'concurrent.futures', 'email.parser', 'email.policy',
]
for _pkg in ('webview', 'clr_loader', 'pythonnet', 'frida', 'openpyxl', 'psutil', 'requests'):
    tmp_ret = collect_all(_pkg)
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    [os.path.join(ROOT_DIR, 'launcher', 'heinzhubweb.py')],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx', 'gi',
        'torch', 'torchvision', 'torchaudio', 'scipy', 'pandas', 'numpy',
        'matplotlib', 'PIL', 'cv2', 'tkinter', 'lxml', 'IPython', 'jupyter', 'pytest',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HeinZ',
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
    icon=[os.path.join(ROOT_DIR, 'launcher', 'assets', 'heinz.ico')],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HeinZ',
)
