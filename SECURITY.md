# Privacy and safe sharing / 隐私与安全分享

## 中文

本项目是本地桌面工具，不是凭据管理器，也不是完整的安全审计产品。

以下内容不能公开：

- `%LOCALAPPDATA%\AIUsageMonitorV2` 整个运行数据目录，尤其是 `codex-home`。
- 官方客户端的 `.codex`、`.claude`、`auth.json`、凭据、Cookie、授权链接和验证码。
- `claude-bridge.json` 恢复记录：可能包含旧的自定义命令和本机路径。
- 本机设置、错误日志、历史数据库、CSV 导出、真实账号截图和测试输出。
- `.env`、私钥、访问令牌，以及含这些内容的 Git 历史和压缩包。

原始状态栏输入可能包含敏感信息；接收器只保留明确允许的额度和估算字段，不保存原始输入。独立 Codex 配置仍由官方客户端保存认证信息，不得公开。90 天历史清理发生在保存新观测时，并非后台定时安全擦除。

`.gitignore` 只能减少误添加，不能检查文件内容或清除历史。不要强制添加被忽略的运行数据；发布前检查暂存区和待上传压缩包。

普通 Bug 请提供系统、应用和官方客户端版本、复现步骤及脱敏错误提示。不要附整个数据目录、真实授权链接或令牌；截图前隐藏账号、路径和个人用量。

安全问题优先通过 GitHub Private vulnerability reporting 报告（如果维护者已启用）。没有私密通道时，可先创建不含敏感细节的联系请求，不要在公开 Issue 中贴凭据。

若凭据已经泄露，应先在对应服务撤销或轮换，再清理 Git 历史、Release 附件及缓存副本。只删除当前文件不足以撤销访问权限。

## English

This local desktop utility is not a credential vault or a comprehensive security audit product.

Never publish:

- The complete `%LOCALAPPDATA%\AIUsageMonitorV2` runtime folder, especially `codex-home`.
- Official client profiles (`.codex`, `.claude`), `auth.json`, credentials, cookies, authorization URLs or verification codes.
- `claude-bridge.json`: recovery data can contain previous custom commands and machine paths.
- Local settings, crash logs, databases, CSV exports, real-account screenshots or test output.
- Environment files, private keys, access tokens, or Git history and archives containing them.

Raw status-line input can be sensitive. The helper persists only allowed quota and estimate fields, not raw input. The official Codex client retains authentication state in its separate profile, which must remain private. History retention is pruned when saving new observations, not by scheduled secure erasure.

`.gitignore` reduces accidental additions; it does not inspect content or erase history. Do not force-add runtime data. Review staged files and release archives before publishing.

For ordinary bugs, provide OS, app and official client versions, reproduction steps and sanitized errors. Never attach whole data folders, authorization URLs or tokens. Redact accounts, paths and personal usage from screenshots.

Use GitHub Private vulnerability reporting if enabled by the maintainer. If no private channel exists, request one without disclosing sensitive details in a public issue.

If credentials are exposed, revoke or rotate them with the provider first, then clean Git history, release assets and cached copies. Deleting the current file alone does not revoke access.
