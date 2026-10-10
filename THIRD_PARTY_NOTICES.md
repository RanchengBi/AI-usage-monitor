# Third-party notices / 第三方告知

AI Usage Monitor is an independent community tool, not an OpenAI or Anthropic product. 自有代码采用 MIT；第三方组件各自保留许可。

| Component / 组件 | Version / 版本 | License / 许可 |
| --- | --- | --- |
| CPython | 3.12.14 | PSF and included component notices |
| QtBase, QtTranslations | 6.10.2 | LGPLv3 option and included component licenses |
| PySide6, Shiboken6 | 6.10.2 | LGPLv3 option and included component licenses |
| PyInstaller bootloader | 6.19.0 | GPL with bootloader exception |
| OpenSSL runtime | 3.5.8 | Apache-2.0 |
| libffi | runtime dependency | MIT |
| SQLite | 3.53.1 | Public domain |
| bzip2, XZ/liblzma | runtime dependencies | bzip2 license; public-domain/0BSD portions |
| Microsoft VC/UCRT runtime | bundled redistributable components | Microsoft redistribution terms |
| Inno Setup / Chinese translation | build tool | Inno Setup license and original attribution |

This application uses Qt under LGPLv3. Complete corresponding QtBase, QtTranslations and PySide/Shiboken source archives accompany the release. The libraries are unmodified and dynamically linked. Library replacement/relinking and reverse engineering for debugging modifications are permitted. See [DEPENDENCY_BUILD.md](DEPENDENCY_BUILD.md), [DEPENDENCY_SOURCES.json](DEPENDENCY_SOURCES.json) and the release's third-party-source archive.

本程序按 LGPLv3 使用 Qt。Release 同时提供对应库的完整源码；库采用动态链接，未修改源码，允许替换兼容库并调试修改。详见依赖说明。完整许可及组件版权告知随安装器保存在 `licenses/`，仓库副本位于 `assets/licenses/`。其中上游作者的姓名、邮箱与网址是必须保留的归属信息，不是使用者的账号数据。

The installer preserves license texts under `licenses/`; repository copies are under `assets/licenses/`. QtBase attribution files and their referenced source notices are preserved from the official archives, including notices for code that may be disabled on Windows. Retaining extra notices does not mean extra libraries are shipped. Windows fonts and provider clients are not redistributed. The application icon is generated from basic shapes in build.py.
