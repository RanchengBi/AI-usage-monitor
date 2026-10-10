"""Reproducible Windows build: python build.py --iscc PATH_TO_ISCC.exe."""
import argparse
from importlib.metadata import distribution
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent / "work"
DIST = WORK / "v2-dist"
OUTPUT = ROOT.parent / "outputs"


def run(args):
    subprocess.run([str(a) for a in args], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iscc", default="")
    parser.add_argument("--skip-freeze", action="store_true")
    args = parser.parse_args()
    if sys.platform != "win32":
        raise SystemExit("Build the Windows release on Windows.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = ROOT / "assets"
    if not args.skip_freeze:
        from PySide6.QtCore import QLibraryInfo, Qt
        from PySide6.QtGui import QColor, QImage, QPainter
        image = QImage(256, 256, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#087D71"))
        painter.drawRoundedRect(0, 0, 256, 256, 52, 52)
        painter.setBrush(QColor("#FFFFFF"))
        for x, top in ((53, 139), (111, 97), (169, 55)):
            painter.drawRoundedRect(x, top, 35, 198 - top, 9, 9)
        painter.end()
        if not image.save(str(assets / "app.ico")):
            raise RuntimeError("Could not create application icon")
        shutil.copy2(Path(QLibraryInfo.path(QLibraryInfo.TranslationsPath)) / "qtbase_zh_CN.qm", assets / "qtbase_zh_CN.qm")
        common = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
                  "--distpath", DIST, "--workpath", WORK / "v2-build", "--specpath", WORK / "v2-spec"]
        run(common + ["--name", "UsageBridge", "--contents-directory", "_bridge_internal", ROOT / "claude_bridge.py"])
        run(common + ["--name", "AIUsageMonitor", "--windowed", "--icon", assets / "app.ico",
                      "--add-data", str(assets / "app.ico") + ";assets",
                      "--add-data", str(assets / "qtbase_zh_CN.qm") + ";assets", ROOT / "app.py"])
        app_dist = DIST / "AIUsageMonitor"
        shutil.copy2(DIST / "UsageBridge/UsageBridge.exe", app_dist / "UsageBridge.exe")
        shutil.copytree(DIST / "UsageBridge/_bridge_internal", app_dist / "_bridge_internal", dirs_exist_ok=True)
        for name in ("README.md", "README.zh-CN.md", "README.en.md", "LICENSE", "SECURITY.md",
                     "THIRD_PARTY_NOTICES.md", "DEPENDENCY_BUILD.md", "DEPENDENCY_SOURCES.json", "LICENSE_REVIEW.md", "UPLOAD_GITHUB.md", "SHARING_AUDIT.md", "CHANGELOG.md"):
            shutil.copy2(ROOT / name, app_dist / name)
        # License texts accompany the unmodified, dynamically linked Qt libraries.
        pyside = Path(__import__("PySide6").__file__).parent
        if (pyside / "licenses").exists():
            shutil.copytree(pyside / "licenses", app_dist / "licenses/Qt", dirs_exist_ok=True)
        for package in ("PySide6", "PySide6_Essentials", "PySide6_Addons", "shiboken6", "pyinstaller"):
            dist = distribution(package)
            for file in dist.files or []:
                if '/licenses/' in str(file).replace('\\', '/'):
                    destination = app_dist / "licenses" / package / Path(str(file)).name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(dist.locate_file(file), destination)
        if (assets / "licenses").exists():
            shutil.copytree(assets / "licenses", app_dist / "licenses", dirs_exist_ok=True)
    # Qt 6.10 on Windows imports the OS ICU API (unversioned exports). Some
    # portable Python distributions expose an unrelated ICU 78 on PATH; the
    # freezer can incorrectly collect it and shadow the Windows implementation.
    # Use the supported Windows OS DLL rather than redistributing that collision.
    internal = DIST / "AIUsageMonitor" / "_internal"
    # This Widgets application uses only QtBase. Restrict auto-collected plugins
    # and libraries so optional PDF/QML/virtual-keyboard modules are not shipped.
    qt_root = internal / 'PySide6'
    # The Widgets UI does not use the optional software OpenGL rasterizer.
    (qt_root / 'opengl32sw.dll').unlink(missing_ok=True)
    qt_dlls = {'qt6core.dll', 'qt6gui.dll', 'qt6widgets.dll', 'qt6network.dll', 'qt6test.dll'}
    plugins = {'platforms/qwindows.dll', 'platforms/qminimal.dll', 'platforms/qoffscreen.dll',
               'styles/qmodernwindowsstyle.dll', 'imageformats/qico.dll', 'imageformats/qjpeg.dll',
               'imageformats/qgif.dll', 'networkinformation/qnetworklistmanager.dll',
               'tls/qschannelbackend.dll', 'tls/qcertonlybackend.dll'}
    for candidate in qt_root.glob('Qt6*.dll'):
        if candidate.name.lower() not in qt_dlls:
            candidate.unlink()
    for candidate in (qt_root / 'plugins').rglob('*.dll'):
        if candidate.relative_to(qt_root / 'plugins').as_posix().lower() not in plugins:
            candidate.unlink()
    # The monitor does not use Qt Virtual Keyboard (commercial/GPLv3).
    # QtGui's automatic plugin collection can include it indirectly. Exclude
    # both the unused plugin and library instead of silently shipping it.
    for candidate in internal.rglob('*'):
        if candidate.is_file() and candidate.name.lower() in {'qtvirtualkeyboardplugin.dll', 'qt6virtualkeyboard.dll'}:
            candidate.unlink()
    for collision in [internal / "icuuc.dll", *internal.glob("icudt*.dll")]:
        if collision.is_file():
            collision.unlink()
    compiler = args.iscc or shutil.which("ISCC.exe") or str(WORK / "inno/ISCC.exe")
    if not Path(compiler).exists():
        raise SystemExit("Install Inno Setup 6.5+ and supply --iscc PATH. Frozen app is available in work/v2-dist.")
    compiler = str(Path(compiler).resolve())
    run([compiler, "/DAppDist=" + str(DIST / "AIUsageMonitor"), "/DOutputPath=" + str(OUTPUT), ROOT / "installer.iss"])


if __name__ == "__main__":
    main()
