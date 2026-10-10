# Font and license review / 字体与许可检查

## v2.2.1 / 2026-10-10


### 字体与界面素材

程序在 Windows 上按名称调用 Segoe UI、Microsoft YaHei / Microsoft YaHei UI；无界面测试也只从本机 Windows Fonts 目录读取字体。源码上传包不包含 TTF、TTC、OTF、WOFF 或其他字体文件，构建脚本没有复制 Windows 字体的步骤。

微软允许 Windows 应用使用系统字体显示界面，但通常不允许把这些字体另行打包分发。当前“调用用户系统字体、不附带字体文件”的方式符合该使用情形；不要把 Windows 字体复制到项目、安装包或网站。此判断依据[微软字体使用与再分发说明](https://learn.microsoft.com/en-us/typography/fonts/font-faq)。

`assets/app.ico` 是 `build.py` 用基本几何图形绘制的项目图标，不使用第三方品牌 Logo。界面箭头和关闭符号由系统字体渲染。此次源码包不含用户截图、网上下载的插画或照片。


### 发布处理

- 自有代码和图标保留 MIT；第三方库不改为 MIT。
- 新构建仅保留实际所需 QtBase 模块与插件，移除未使用的虚拟键盘、PDF、QML、Quick、SVG 等模块。
- 同一 Release 附完整 QtBase、QtTranslations、PySide/Shiboken 6.10.2 官方源码归档、来源及校验值；安装目录附许可和上游版权告知。
- Qt 采用 LGPLv3 动态链接方式，允许库替换与为调试修改进行逆向工程。操作及重建说明见 [DEPENDENCY_BUILD.md](DEPENDENCY_BUILD.md)。
- Python 及其随附许可、OpenSSL、libffi、XZ、bzip2、Inno Setup 和 Qt 源码中的组件告知均保留。原始署名和公开联系地址是上游归属信息。
- 这些处理适用于本次 v2.2.1 构建；不把早期安装器视为同一构建，也不是所有未来改动的法律保证。

## English

The app requests locally installed Windows fonts; no Windows font files are redistributed. The icon is drawn from project-owned geometric shapes. See [Microsoft's font FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq).

Project-owned code remains MIT. The v2.2.1 build retains only the required QtBase libraries/plugins, excluding unused Virtual Keyboard, PDF, QML, Quick and SVG modules. The same Release supplies complete official QtBase, QtTranslations and PySide/Shiboken 6.10.2 source archives with origins/hashes; the installer includes licenses and upstream notices. Qt is dynamically linked under LGPLv3 with replacement and debugging-modification rights preserved; see [DEPENDENCY_BUILD.md](DEPENDENCY_BUILD.md). Python/runtime and additional dependency notices are retained. Public upstream attribution is not user account data. This describes this build, not a legal guarantee for every future modification or an endorsement of older installers.
