# Font and license review / 字体与许可检查

Review date / 检查日期：2026-10-10。Scope / 范围：v2.2.0 源码上传包及本机构建配置。

## 中文

### 字体与界面素材

程序在 Windows 上按名称调用 Segoe UI、Microsoft YaHei / Microsoft YaHei UI；无界面测试也只从本机 Windows Fonts 目录读取字体。源码上传包不包含 TTF、TTC、OTF、WOFF 或其他字体文件，构建脚本没有复制 Windows 字体的步骤。

微软允许 Windows 应用使用系统字体显示界面，但通常不允许把这些字体另行打包分发。当前“调用用户系统字体、不附带字体文件”的方式符合该使用情形；不要把 Windows 字体复制到项目、安装包或网站。此判断依据[微软字体使用与再分发说明](https://learn.microsoft.com/en-us/typography/fonts/font-faq)。

`assets/app.ico` 是 `build.py` 用基本几何图形绘制的项目图标，不使用第三方品牌 Logo。界面箭头和关闭符号由系统字体渲染。此次源码包不含用户截图、网上下载的插画或照片。

### 项目与第三方许可证

| 内容 | 处理方式 |
| --- | --- |
| 本项目自有源码和图标 | MIT；保留 LICENSE 中的版权和许可声明，可使用、修改、分发及商业使用 |
| Windows 字体 | 仅调用本机已安装字体，不再分发字体文件 |
| Inno Setup 中文翻译 | 保留原文件的译者及公开联系方式，附 Inno Setup 原始许可证；不是本项目作者的个人资料 |
| Python | 独立 PSF 及相关组件许可；保留 Python 许可证 |
| PySide6 / Shiboken6 / Qt | 不被本项目 MIT 覆盖；按适用的 LGPLv3、GPLv3 或组件许可证处理 |
| PyInstaller | GPL 及 bootloader 例外；该例外允许应用采用自身许可证，但不豁免 Qt 等依赖义务 |

### 源码上传与 EXE 发布必须区分

此次上传包只分发项目源码、文档、自有图标、安装翻译和许可文本；不附 EXE、DLL、Python/Qt 运行库或编译后的 Qt 翻译文件。源码运行时使用用户安装的 PySide6 翻译资源，构建时再从依赖复制所需资源。

检查还发现旧构建自动带入了未使用的 `Qt6VirtualKeyboard.dll` 及其输入插件；该模块采用商业/GPLv3许可。源码中的构建脚本已增加排除这两个文件的处理，但本次没有重发旧安装包。参见 [Qt Virtual Keyboard 许可](https://doc.qt.io/qt-6/qtvirtualkeyboard-index.html#licenses-and-attributions)。

已有构建保留了部分许可证，并采用可替换 DLL 的动态链接，但不能仅凭这些措施及上游链接就宣称 EXE 的 LGPL 分发义务已全部完成。**旧安装包不作为本次 GitHub 发布附件；其完整对应依赖源码提供方案及逐组件版权告知尚未完成本次核验。**

若要在 GitHub Releases 另外公开安装包，需针对实际捆绑版本落实完整对应库源码及构建信息的提供方式、保留组件版权告知和许可文本，并允许用户替换/重新链接相应库及为调试修改而进行逆向工程。项目源码不等于 Qt/PySide6 的完整对应源码；普通上游主页链接也不等于已履行源码提供义务。参见 [Qt 官方 LGPL 义务说明](https://www.qt.io/development/open-source-lgpl-obligations)及 [PyInstaller 6.19.0 许可说明](https://pyinstaller.org/en/v6.19.0/license.html)。

本文件记录实际检查与已知缺口，不是对所有用途、所有依赖或未来版本的法律保证。

## English

### Fonts and artwork

The Windows UI requests Segoe UI and Microsoft YaHei / Microsoft YaHei UI by name. Headless tests load fonts only from the local Windows Fonts directory. The source upload contains no TTF, TTC, OTF, WOFF or other font files, and the build script does not copy Windows fonts.

Microsoft permits Windows applications to render UI using system fonts, while generally restricting redistribution of those font files. Calling locally installed fonts without shipping them fits that use case. Do not copy Windows fonts into this repository, an installer or a website. See [Microsoft's font redistribution FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq).

The project icon is drawn from basic shapes by `build.py`; it is not a third-party brand logo. UI arrows and close symbols use system fonts. This source archive contains no personal screenshots, downloaded illustrations or photographs.

### License boundaries

Project-owned code and the icon use MIT. Preserve the copyright and permission notice; use, modification, redistribution and commercial use are permitted. Python retains PSF/component licenses. PySide6, Shiboken6 and Qt retain applicable LGPLv3/GPLv3/component licenses. PyInstaller's bootloader exception allows an application to use its own license but does not waive dependency obligations. The Inno Setup translation retains upstream attribution and public contact details, together with the Inno Setup license; these are not the project owner's personal details.

### Source uploads versus binary releases

This upload includes project source, documentation, the project icon, installer translation and license texts. It contains no executables, DLLs, Python/Qt runtimes or compiled Qt translations. Source runs use the installed PySide6 translation resources; builds copy resources from installed dependencies.

The older build automatically included the unused `Qt6VirtualKeyboard.dll` and its input plugin, a commercial/GPLv3 module. The source build script now excludes both files; this review does not reissue the old installer. See [Qt Virtual Keyboard licensing](https://doc.qt.io/qt-6/qtvirtualkeyboard-index.html#licenses-and-attributions).

The existing build preserves some license texts and uses replaceable, dynamically linked DLLs. Those steps and upstream links alone do not establish complete LGPL compliance. **The old installer is excluded from this GitHub delivery. Corresponding dependency source provision and a component-by-component notice review remain unverified.**

Before publishing binaries in GitHub Releases, fulfill corresponding library source/build-information obligations for the bundled versions, retain component notices and licenses, and permit replacement/relinking and reverse engineering for debugging modifications. This application's source is not the complete corresponding Qt/PySide6 source, and a general upstream homepage link is not evidence of fulfillment. See [Qt's LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations) and [PyInstaller 6.19.0 licensing](https://pyinstaller.org/en/v6.19.0/license.html).

This is a record of checks and known gaps, not a legal guarantee for every use, dependency or future release.
