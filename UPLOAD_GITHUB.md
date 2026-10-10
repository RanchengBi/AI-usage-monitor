# Upload guide / GitHub 上传指南

## 中文

1. 解压带有 `Source_Reviewed` 标记的源码 ZIP。
2. 在 GitHub 新建空仓库，以解压后含 `README.md`、`app.py`、`LICENSE` 的目录作为仓库根目录。上传该目录里的文件，包含 `.gitignore`；不要把整个外层工作文件夹上传。
3. 仓库简介可使用：**免费开源的 Windows AI 额度监控工具，支持 Codex、Claude Code、中英文、托盘悬浮窗与额度提醒。**
4. 不上传 `.codex`、`.claude`、运行数据、账号文件、缓存、数据库、日志、CSV、真实截图或 `.git`。本包不包含旧提交历史；新提交仍会公开你所选的 GitHub 账号身份。若用本地 Git，请使用 GitHub 提供的隐私邮箱，而非私人邮箱。
5. 本仓库发布审核后的源码。EXE、应用源码和对应依赖源码随 v2.2.1 Release 发布；以后发布应一并维护源码、许可和校验文件，见 [LICENSE_REVIEW.md](LICENSE_REVIEW.md)。

欢迎使用、反馈 Bug、完善翻译及提交 Pull Request。反馈前请移除账号、密钥、授权链接、个人路径和真实用量；安全问题见 [SECURITY.md](SECURITY.md)。

## English

1. Extract the source ZIP marked `Source_Reviewed`.
2. Create an empty GitHub repository. Use the extracted directory containing `README.md`, `app.py` and `LICENSE` as its root. Upload its contents, including `.gitignore`, rather than the outer working folder.
3. Suggested description: **A free, open-source Windows AI usage monitor for Codex and Claude Code, with English/Chinese UI, tray and floating windows, and quota alerts.**
4. Do not upload provider profiles, runtime/account files, caches, databases, logs, CSV exports, real screenshots or `.git`. This archive contains no old Git history; new commits still expose the GitHub identity you choose. With local Git, use GitHub's private noreply address instead of a personal email.
5. This repository publishes the reviewed source. The v2.2.1 Release provides the EXE, application source and corresponding dependency sources; preserve source, notices and checksums in future releases. See [LICENSE_REVIEW.md](LICENSE_REVIEW.md).

Usage, bug reports, translation improvements and pull requests are welcome. Remove accounts, secrets, authorization links, personal paths and real usage from reports. See [SECURITY.md](SECURITY.md) for security issues.
