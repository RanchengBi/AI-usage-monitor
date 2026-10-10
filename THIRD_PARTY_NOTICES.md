# Third-party software

AI Usage Monitor v2 is an independent local utility. It is not an official OpenAI or Anthropic application.

Project-owned source code is licensed under the MIT license in LICENSE. This does not relicense any third-party component or replace its notices and distribution obligations. Upstream copyright names and contact addresses in license and translation files are intentional attribution, not user account data.

The older local Windows build contains unmodified Python 3.12 (PSF license), PySide6 / Shiboken6 6.10.2 and Qt 6.10.2 (open-source LGPLv3/GPLv3 and applicable component licenses), and the PyInstaller 6.19.0 bootloader (GPL with the PyInstaller bootloader exception). Qt is dynamically linked; the `_internal` DLLs can be replaced with compatible modified builds. This source delivery does not include an installer or certify complete binary-distribution compliance; see LICENSE_REVIEW.md. No proprietary Windows fonts are redistributed.

Upstream source, licenses and build instructions:
- Python: https://www.python.org/downloads/source/ and https://docs.python.org/3/license.html
- PySide6: https://code.qt.io/cgit/pyside/pyside-setup.git/ and https://doc.qt.io/qtforpython-6/licenses.html
- Qt: https://download.qt.io/archive/qt/6.10/6.10.2/single/ and https://www.qt.io/licensing/open-source-lgpl-obligations
- PyInstaller: https://github.com/pyinstaller/pyinstaller/tree/v6.19.0 and https://pyinstaller.org/en/stable/license.html

The installer is built with Inno Setup. Its language translation is from the official Inno Setup translations repository (Zhenghan Yang, Simplified Chinese): https://github.com/jrsoftware/issrc/tree/main/Files/Languages

Provider clients are not redistributed. Users install official Codex and Claude Code separately. No provider account credentials, cookies, conversations, or machine-specific test data are included in this release.

## Source review / 源码发布说明

The reviewed source upload omits compiled Qt translations and all third-party runtimes. Source runs obtain Qt translations from installed PySide6. The Inno Setup license is retained in [assets/licenses/Inno-Setup-LICENSE.txt](assets/licenses/Inno-Setup-LICENSE.txt); the original translation attribution is preserved.

本次源码包不附 Qt 编译翻译或任何第三方运行库。旧构建自动收集了未使用的 Qt Virtual Keyboard；构建脚本现已排除其 DLL 和输入插件。旧 EXE 的依赖对应源码及完整版权告知仍需在公开分发前补齐，详见 [LICENSE_REVIEW.md](LICENSE_REVIEW.md)。Windows 系统字体仅按名称调用，不复制分发。

The build script now excludes the unused Qt Virtual Keyboard DLL and input plugin that the older build collected automatically. Corresponding dependency source and complete notices for binary releases remain separate obligations; see [LICENSE_REVIEW.md](LICENSE_REVIEW.md). Windows fonts are requested locally, not redistributed.
