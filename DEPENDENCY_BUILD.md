# Dependency source and replacement / 依赖源码与替换

## 中文

v2.2.1 的 [GitHub Release](https://github.com/RanchengBi/AI-usage-monitor/releases/tag/v2.2.1) 同时提供安装器、应用源码、`AIUsageMonitor_ThirdPartySources_v2.2.1.zip` 和 SHA-256 校验文件。第三方源码附件含官方未修改的 QtBase 6.10.2、QtTranslations 6.10.2、PySide/Shiboken 6.10.2 完整发布源码归档，不是仅提供主页链接。文件来源及 SHA-256 见 [DEPENDENCY_SOURCES.json](DEPENDENCY_SOURCES.json)。普通用户只需安装 EXE。

本程序使用 Qt 的 LGPLv3 许可选项；项目自有代码仍为 MIT。对应库采用动态链接，未修改库源码，不限制为调试库修改而进行的逆向工程。你可以替换兼容的修改版库，也可以从应用源码重新构建。发布附件中的源码和许可供所有收到安装包的人免费下载。

库版本：QtBase / QtTranslations / PySide6 / Shiboken6 6.10.2；构建工具 PyInstaller 6.19.0。Windows x64 发布使用 CPython 3.12.14、MSVC 运行库及 Inno Setup。Qt 模块限于 Core、Gui、Widgets、Network、Test 和列明的 QtBase 插件，不包含 Qt Virtual Keyboard、PDF、QML、Quick、SVG 等可选模块。实际库及插件清单由 `build.py` 控制。

重建建议：

1. 安装 Windows SDK、MSVC x64 C++ 工具链、CMake、Ninja 和兼容 Python。解压依赖源码附件中的归档。其 README、CMake 文件、`coin_build_instructions.py` 和构建脚本保留在源码归档中。
2. 在 x64 Native Tools 命令行，以 QtBase 源码为源目录，在单独构建目录运行 `configure.bat -opensource -confirm-license -release -nomake examples -nomake tests -prefix C:\qt-custom`，然后运行 `cmake --build . --parallel` 与 `cmake --install .`。具体编译器要求以归档中的平台说明为准；这不是逐字节可复现构建承诺。
3. 使用 PySide 源码中的构建说明，例如 `python setup.py bdist_wheel --qtpaths=C:\qt-custom\bin\qtpaths6.exe --standalone --build-type=all`。确保需要的 Core、Gui、Widgets、Network、Test 绑定存在；安装生成的 PySide6 / Shiboken6 wheel。Qt 翻译可使用同版本 `lrelease` 从提供的 `.ts` 重新生成。
4. 使用仓库 `build.py` 及 Inno Setup 重新打包应用。若使用修改版库，不要让 `pip install -r requirements.txt` 又把它覆盖成官方 wheel。

直接替换时先从托盘退出应用并备份安装目录；在 `_internal/PySide6` 中替换 ABI 兼容的 Qt DLL 及相匹配的插件，必要时同时替换 `_internal/shiboken6` 和 Python 绑定。保持同一架构、Python ABI 与 Qt/PySide 版本体系，不要单独混用不兼容 DLL。应用没有库签名锁定；不兼容替换可能无法启动，可恢复备份或重装。

## English

The [v2.2.1 release](https://github.com/RanchengBi/AI-usage-monitor/releases/tag/v2.2.1) provides the installer, application source, `AIUsageMonitor_ThirdPartySources_v2.2.1.zip` and SHA-256 checksums. The dependency archive contains the complete, unmodified official QtBase, QtTranslations and PySide/Shiboken 6.10.2 source release archives, not just homepage links. See [DEPENDENCY_SOURCES.json](DEPENDENCY_SOURCES.json) for origins and hashes. Ordinary users only need the installer.

Qt libraries are used under LGPLv3; project-owned code remains MIT. Libraries are dynamically linked and their source is unmodified. Reverse engineering for debugging library modifications is not restricted. You may replace compatible libraries or rebuild the application with modified dependencies. Dependency source and notices are available without charge to all installer recipients.

The Windows x64 build uses CPython 3.12.14, Qt/PySide/Shiboken 6.10.2, PyInstaller 6.19.0, the MSVC runtime and Inno Setup. Only QtBase Core, Gui, Widgets, Network, Test and the plugins allowed by `build.py` are shipped. Optional Virtual Keyboard, PDF, QML, Quick and SVG modules are excluded.

Install the Windows SDK, MSVC x64 C++ tools, CMake, Ninja and a compatible Python. Extract the source archives and follow their included READMEs, CMake files and build scripts. In an out-of-source QtBase build directory, use the source `configure.bat` with `-opensource -confirm-license -release -nomake examples -nomake tests -prefix C:\qt-custom`, then `cmake --build . --parallel` and `cmake --install .`. Build PySide/Shiboken wheels using the included instructions, for example `python setup.py bdist_wheel --qtpaths=C:\qt-custom\bin\qtpaths6.exe --standalone --build-type=all`. Include the five bindings used by the application. Translation `.ts` files can be compiled with matching `lrelease`. Install the resulting wheels and rebuild the app with `build.py`; do not overwrite custom wheels by reinstalling pinned official dependencies. These are rebuild directions, not a bit-for-bit reproducibility claim.

For replacement, quit the app and back up the installation. Replace ABI-compatible Qt DLLs and matching plugins under `_internal/PySide6`; replace the bindings and `_internal/shiboken6` together when necessary. Keep architecture, Python ABI and Qt/PySide versions compatible. There is no library signature lock. Restore the backup or reinstall if incompatible replacements fail to launch.
