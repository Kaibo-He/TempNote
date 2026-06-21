#!/usr/bin/env python3
"""打包 TempNote 为 exe，输出到 dist/v{version}/TempNote.exe

生成的 exe 默认请求管理员权限（启动时弹出 UAC）。
重新打包同一版本时会先删除 dist/v{version}/ 与 PyInstaller 缓存，再生成新 exe。

用法:
    python build.py           # 交互输入版本号
    python build.py 1.1.0     # 指定版本号
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    print(f">>> {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT, check=check)


def _read_version() -> str:
    if len(sys.argv) > 1:
        version = sys.argv[1].strip().lstrip("vV")
    else:
        version = input("版本号 (如 1.1.0): ").strip().lstrip("vV")
    if not VERSION_RE.fullmatch(version):
        print("错误：版本号格式应为 x.x.x，例如 1.1.0")
        sys.exit(1)
    return version


def _ensure_deps() -> None:
    _run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "pyinstaller"])
    _run([sys.executable, "-c", "import PySide6; print('PySide6 OK')"])


def _write_spec() -> Path:
    spec_dir = ROOT / "build"
    spec_dir.mkdir(exist_ok=True)
    spec_path = spec_dir / "TempNote.spec"
    main_py = str(ROOT / "main.py")
    spec_path.write_text(
        """# -*- mode: python ; coding: utf-8 -*-
# 由 build.py 自动生成

a = Analysis(
    [%r],
    pathex=[],
    binaries=[],
    datas=[],
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
    name='TempNote',
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
    uac_admin=True,
)
""" % main_py,
        encoding="utf-8",
    )
    return spec_path


def _clean_version_output(version: str) -> Path:
    """删除同版本旧产物，避免 dist 中残留过时文件。"""
    dist_dir = ROOT / "dist" / f"v{version}"
    if dist_dir.exists():
        print(f"清理旧产物: {dist_dir}")
        shutil.rmtree(dist_dir)

    work_dir = ROOT / "build" / "pyinstaller"
    if work_dir.exists():
        print(f"清理 PyInstaller 缓存: {work_dir}")
        shutil.rmtree(work_dir)

    dist_dir.mkdir(parents=True, exist_ok=True)
    return dist_dir


def main() -> None:
    version = _read_version()
    dist_dir = _clean_version_output(version)

    print(f"打包 TempNote v{version} → {dist_dir}（exe 将以管理员身份运行）")
    _ensure_deps()

    spec_path = _write_spec()
    _run([
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(ROOT / "build" / "pyinstaller"),
        "--noconfirm",
    ])

    exe = dist_dir / "TempNote.exe"
    if not exe.is_file():
        print("错误：未找到 TempNote.exe，打包可能失败")
        sys.exit(1)

    size_mb = exe.stat().st_size / (1024 * 1024)
    print(f"\n完成: {exe}")
    print(f"大小: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
