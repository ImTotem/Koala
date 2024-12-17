import platform
from pathlib import Path
import plyer

# plyer 모듈의 설치 경로 찾기
plyer_path = Path(plyer.__file__).parent

block_cipher = None

a = Analysis(
    ['koala/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('koala', 'koala'),
        (str(plyer_path), 'plyer'),  # plyer 전체를 포함
    ],
    hiddenimports=[
        'koala',
        'koala.conf',
        'koala.domain',
        'koala.domain.assignment',
        'koala.domain.auth',
        'koala.domain.view',
        'koala.utils',
        'koala.app',
        'plyer.platforms',  # plyer 플랫폼 모듈
        'plyer.platforms.macosx.notification',  # macOS 구현
        'plyer.platforms.win.notification',     # Windows 구현
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Koala',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

if platform.system() == 'Darwin':
    app = BUNDLE(
        exe,
        name='Koala.app',
        icon=None,
        bundle_identifier=None,
    )
