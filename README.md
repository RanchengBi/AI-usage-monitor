# AI Usage Monitor v2.2.0

**免费 · 开源 · 欢迎使用！** 本软件本身不收取使用费，无广告。欢迎下载、分享、反馈问题和参与改进。项目自有代码采用 [MIT](LICENSE)；OpenAI / Anthropic 的账号、订阅和 API 费用由相应平台另行收取。

**Free and open source — everyone is welcome!** This software is free to use and contains no ads. Download, share, report issues and contribute improvements. Project-owned code is licensed under [MIT](LICENSE); provider accounts, subscriptions and API charges are separate.

[简体中文独立版](README.zh-CN.md) · [English edition](README.en.md) · [字体与许可 / Licenses](LICENSE_REVIEW.md) · [上传指南 / Upload guide](UPLOAD_GITHUB.md)

Windows 桌面 AI 额度监控工具，支持简体中文和 English，使用 Python + PySide6 构建。

A Windows desktop utility for monitoring AI subscription usage, built with Python and PySide6. Available in English and Simplified Chinese.

[中文说明](#中文说明) · [English guide](#english-guide) · [MIT license](LICENSE) · [Privacy / 隐私](SECURITY.md)

独立社区项目，与 OpenAI、Anthropic 无隶属关系。项目处于早期阶段，平台与客户端更新可能影响接入。

Independent community project, not affiliated with OpenAI or Anthropic. This is an early release; provider and client updates may affect compatibility.

## 中文说明

### 项目介绍与参与

在桌面查看 Codex 和 Claude Code 返回的订阅额度，减少在多个客户端之间切换。支持中英文、托盘、可贴边悬浮窗、剩余额度提醒及本地历史导出。

欢迎通过 Issue 提交脱敏的复现步骤，通过 Pull Request 改进代码、文档和翻译。提交内容应为你有权贡献的内容，并接受本项目的 MIT 许可；第三方内容须保留自身许可和署名。不要提交真实账号、API 密钥、授权链接或个人数据。

“免费”指本项目不收使用费；MIT 仍允许遵守许可条件的商业使用和再分发。本项目不提供 AI 订阅、不绕过平台额度，也不代表 OpenAI 或 Anthropic。

本次源码上传包不附安装器或第三方运行库。先按下文从源码运行；二进制发布的已知许可事项见 [许可检查](LICENSE_REVIEW.md)。

### v2.2 新增：额度提醒与清晰托盘菜单

- 额度提醒默认开启，可在主窗口底部或托盘菜单开关。收到新数据时，剩余达到或低于 50%、20%、10% 分别通知；点击通知打开主窗口。
- Codex 和 Claude Code 的每个返回额度窗口分别计算，包含 Plus 账号返回的 5 小时额度和每周额度，不按套餐名称过滤。平台未提供的额度不能推算；普通 ChatGPT 聊天额度仍未接入。
- 每个周期每档只提醒一次，重启保留记录。一次刷新跳过多个档位只提醒最紧急一档；首次连接已低于阈值也提醒。新周期重新计数；未提供重置时间时，额度回升到 50% 以上才重新计数。
- 旧数据、已过期额度和缺失数据不提醒。Codex 跟随每 60 秒刷新；Claude 跟随终端状态栏活动。程序需保持运行，Windows 勿扰/通知设置可能抑制通知。
- 托盘菜单使用独立的深色背景和浅色文字，修复系统深色主题与全局文字颜色混用导致的低对比度。

v2.1.1 修复双屏交界处展开悬浮窗时跳屏的问题，并采用更柔和的深灰圆角面板与窄胶囊标签。吸附后保持在原显示器，主动拖动仍可跨屏；兼容旧版保存的位置。

### v2.1 新增：托盘、贴边悬浮窗与登录恢复

- 默认最小化及点击关闭按钮会收进 Windows 右下角托盘，继续更新数据；单击托盘图标恢复窗口，右键菜单可刷新、开关悬浮窗或**退出程序**。关闭“最小化 / 关闭时收进托盘”可恢复普通窗口行为。没有可用托盘时不会把窗口藏到无法找回的位置。
- 默认显示可置顶的悬浮窗。拖动标题栏移动，靠近屏幕左右边缘松开后自动吸附，鼠标移开约 0.8 秒收成小标签，移入展开。`‹` 按钮立即贴边收起，`↗` 打开主窗口，`×` 仅隐藏悬浮窗。位置及显示偏好会保留；旧数据和过期额度会标明。
- 启动自动检查官方 Codex 客户端保存的登录；已连接时不再显示“登录”按钮。遇到部分认证过期错误会尝试一次官方续期；真正撤销/失效的授权仍需重新登录。最小化、关闭到托盘及退出程序均不会退出账号。Claude 登录继续由官方 Claude Code 保存，“等待活动”不代表需要重新登录。
- 重复打开程序会唤回已有窗口。语言修改后请从托盘菜单**退出程序**再打开。
- 更新前先退出旧程序，再运行新安装包覆盖安装；不需要先卸载，也不需要删除数据或退出账号。数据目录继续使用 `AIUsageMonitorV2`。

### 功能与支持范围

| 功能 | v2.2.0 支持情况 |
| --- | --- |
| Codex 订阅额度 | 通过官方 App Server 读取，每 60 秒刷新；支持手动刷新及多个额度窗口 |
| Codex 官方 IDE 插件用量 | 同一账号、工作空间及订阅计费范围内的使用反映在账号额度中，无需重复相加 |
| Claude Code 订阅额度 | 接收官方终端 `statusLine` 提供的五小时、每周及其他可用额度字段；依赖客户端活动 |
| Claude Code IDE 图形聊天面板 | 使用计入相应账号额度，但本项目**尚未实现图形插件面板的直接自动同步** |
| ChatGPT Work | 官方说明其与 Codex 共享用量；以实际返回的额度窗口为准 |
| 普通 ChatGPT 网页聊天 / GPT 模型消息额度 | **未接入**；Codex 百分比不代表所有 ChatGPT 功能的剩余额度 |
| API Key 账单、Gemini、多账号汇总 | 未接入 |
| 语言、费用与历史 | 安装时可选中英文；月订阅费手动记录；本地历史可导出 CSV |

程序显示官方返回的已用百分比，并计算 `剩余 = 100 - 已用`。不会用消息条数或 Token 数推算订阅额度，也不会把五小时和每周额度相加。

### 安装

系统要求：Windows 10 2004（19041）或更新版本、Windows 11，x64。

1. 若维护者在仓库 **Releases** 发布了安装包，下载 `AIUsageMonitorSetup_v2.2.0.exe`。GitHub **Download ZIP** 仅提供源码；若没有安装包，请按后文从源码运行。
2. 双击安装器，选择 **简体中文** 或 **English**。无需另装 Python，默认按当前用户安装，无需管理员权限。
3. 语言可在程序右上角修改，从托盘退出程序并重新打开后生效。
4. 分别安装所需的官方 Codex、Claude Code 客户端。本项目不附带这两个客户端。

当前安装包未做代码签名。请核对发布来源；若发行版附带 SHA-256 清单，可核对哈希。不要为运行本程序关闭系统安全防护。

### 连接 Codex

1. 安装并更新 [官方 Codex CLI](https://learn.chatgpt.com/docs/cli) 或 Codex 桌面应用。
2. 点击 **登录 Codex**，在官方浏览器页面完成授权。
3. 未找到客户端时，点击 **选择 Codex 程序**，指定官方 `codex.exe`。
4. 登录后自动读取额度；可点击 **立即刷新**。

本程序使用独立的 `codex-home` 登录配置，不复制其他应用的凭据。请确认监控器与 IDE 插件登录的是同一账号和工作空间。API Key 计费与订阅额度不同，本版本不做 API 账单统计。

### 连接 Claude Code

**当前“登录 / 使用说明”按钮只显示说明，不会自动启动登录。**

1. 按 [官方安装指南](https://code.claude.com/docs/en/quickstart) 安装最新版 Claude Code。
2. 在 PowerShell 运行 `claude auth login --claudeai`，在浏览器完成订阅账号登录。也可启动 `claude` 后使用 `/login`。
3. 在监控器中点击 **启用用量接入**。
4. 启动或重新打开 Claude Code **终端会话**，完成首次设置，正常发送一条消息并等待回复。
5. 等待监控器读取数据。它约每 5 秒检查一次本地文件，不是每 5 秒向 Claude 查询账号。

如果 PowerShell 提示找不到 `claude`，先重新打开终端。若通过原生安装器安装且文件在默认位置，可直接运行以下两行，分别登录和启动对话：

```powershell
& "$env:USERPROFILE\.local\bin\claude.exe" auth login --claudeai
& "$env:USERPROFILE\.local\bin\claude.exe"
```

若该位置不存在文件，请先完成官方安装。

**IDE 用户：**在 VS Code 集成终端运行 Claude Code，或在 Claude Code 插件设置中启用 **Use Terminal**，以使用当前状态栏接入。若继续使用图形聊天面板，可输入 `/usage` 查看官方额度；不要把监控器里的旧数据当作实时值。

同一 Claude 订阅账号的网页、桌面及 Claude Code 使用会影响共享额度。状态栏返回的是账号额度观测，会话美元估算只属于该会话，两者不是同一指标。

接入会设置用户级 `statusLine`。已有自定义状态栏时会先询问是否替换并保存恢复记录。项目、组织设置或不同的 `CLAUDE_CONFIG_DIR` 可能使接入不生效。断开或卸载会尝试恢复；若你随后自行修改了状态栏，程序保留新设置及旧备份，不强行覆盖。

### 数据含义与常见问题

- 缺失字段显示“未提供”，不当作 0%。Claude 额度字段需要兼容的客户端和账号，通常在首次模型响应后出现。
- 观测超过 5 分钟标记为旧数据；到达重置时间后不会凭空归零，需等待官方新数据。
- Codex 只显示实际返回的窗口。某账号没有五小时窗口，不代表需要自行补算。
- Claude 显示最后一个发送数据的本机会话，不提供多账号隔离或聚合；切换账号后需等待新数据。
- Claude 会话美元金额是估算，**不是实际账单或订阅扣费**。月费单独手动记录，不做汇率换算，共享套餐只记一次。
- 刷新不会自动发送模型请求；你自己发送的测试消息仍按平台规则计入用量。

| 情况 | 检查方法 |
| --- | --- |
| 一直“等待 Claude 数据” | 登录不等于启动对话。确认已启用接入，在终端完成首次设置并等待一次回复；图形插件面板不属于当前直接接入范围 |
| Claude 数据不更新 | 查看观测时间，检查是否在另一账号、WSL、远程机器或不同配置目录使用，以及项目/组织设置是否覆盖状态栏 |
| 有数据但没有额度 | 更新客户端，并用 Claude 的 `/usage` 检查账号支持情况；官方可能不提供该字段 |
| Codex 未找到 / 离线 | 确认客户端已安装，选择正确的 `codex.exe`，检查网络及登录 |
| 月费与会话估算不同 | 两者来源不同；程序不读取实际账单 |
| 关闭窗口后仍在运行 | 默认收进托盘并继续轮询。要结束程序，请选“退出程序”；Claude 状态栏接入仍可独立写数据，在程序内断开接入即可停止 |

### 隐私与卸载

数据目录：`%LOCALAPPDATA%\AIUsageMonitorV2`。保存设置、最近 90 天的用量历史、Claude 最新观测、状态栏恢复记录及官方 Codex 客户端的独立登录配置。

Claude 接收器仅保留额度、重置时间、观测时间和会话估算费用，不保存原始输入、聊天内容或会话 ID。**整个数据目录都不应上传 GitHub**：Codex 配置可能含凭据，恢复记录和日志可能含本机路径，CSV 会暴露使用习惯。详情见 [SECURITY.md](SECURITY.md)。本程序没有自建分析上报服务；官方客户端仍进行自身的认证及网络请求。

在 Windows **设置 → 应用 → 已安装的应用** 中卸载 **AI Usage Monitor v2**。卸载移除程序并尝试恢复 Claude 状态栏，**保留历史和独立 Codex 登录状态**。

完全清除：先在程序内退出 Codex 登录并断开 Claude 接入，再卸载，最后手动删除上述数据目录。v1 数据目录 `%LOCALAPPDATA%\AIUsageMonitor` 不受影响。

### 从源码运行与构建

使用 Windows x64、Python 3.12，在项目目录打开 PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

运行测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

构建安装器需要 [Inno Setup 6.5+](https://jrsoftware.org/isinfo.php)。将下方路径替换为实际编译器路径：

```powershell
.\.venv\Scripts\python.exe build.py --iscc "C:\path\to\ISCC.exe"
```

也可运行 `build_exe.bat --iscc "C:\path\to\ISCC.exe"` 自动创建环境并构建；该脚本使用默认 Python 3，请先确认其版本。生成的 `work` 和 `outputs` 位于**项目文件夹上一级**。不要单独复制冻结目录中的 EXE，它需要完整依赖文件；普通用户应使用安装器。

开发测试可设置 `AI_USAGE_MONITOR_DATA` 指向临时目录；测试 Claude 设置修改时，还需将 `CLAUDE_CONFIG_DIR` 指向独立测试目录。`--demo --smoke-test --lang zh --snapshot preview.png` 使用标明的演示数据，不连接真实账号。

### 分享到 GitHub

解压准备好的源码包，以 `README.md`、`app.py` 和 `LICENSE` 所在目录为仓库根目录。只上传此项目内容，不要上传外层工作目录、真实数据目录、Python 缓存或其他项目。

建议流程：创建空仓库 → 上传源码 → 检查文件列表 → 创建 Release（可另附经审查的安装器及校验值）。发布前检查截图、日志、CSV 和 Git 历史。`.gitignore` 不能清除已经提交的敏感文件。见 [分享检查记录](SHARING_AUDIT.md)。

项目自身代码按 [MIT](LICENSE) 授权。Qt、Python 等依赖保留各自许可证，MIT 不替代其分发要求。见 [第三方说明](THIRD_PARTY_NOTICES.md)。

## English guide

### About and contributing

See the subscription quotas returned by Codex and Claude Code from your desktop. Features include English/Chinese UI, a notification tray, an edge-docking floating window, remaining-quota alerts and local history export.

Issues with sanitized reproduction steps and pull requests for code, documentation or translations are welcome. Contribute only content you have the right to share under this project's MIT license; retain third-party licenses and attribution. Never include real accounts, API keys, authorization links or personal data.

“Free” means this project charges no usage fee. MIT still permits commercial use and redistribution under its terms. The project does not provide AI subscriptions, bypass provider limits or represent OpenAI or Anthropic.

This source upload includes no installer or third-party runtime. Use the source instructions below; see the [license review](LICENSE_REVIEW.md) for known binary-release requirements.

### New in v2.2: quota alerts and a readable tray menu

- Alerts are on by default; toggle them near the bottom of the main window or in the tray menu. New readings at or below 50%, 20% and 10% remaining trigger notifications. Click a notification to open the main window.
- Every returned Codex and Claude Code quota window is tracked separately, including five-hour and weekly windows returned for Plus accounts. There is no plan-name filter. Missing quotas cannot be inferred; ordinary ChatGPT chat quotas remain unsupported.
- Each threshold alerts once per cycle, with deduplication retained across restarts. Skipping several thresholds produces only the most urgent alert; first connections already below a threshold also notify. New cycles re-arm alerts. Without reset timestamps, recovery above 50% re-arms alerts.
- Stale, expired and missing readings do not notify. Codex follows its 60-second refresh and Claude follows terminal status-line activity. Keep the app running; Windows Do Not Disturb or notification settings may suppress delivery.
- The tray menu now has explicit dark backgrounds and light text, fixing poor contrast from inherited global text colors under a dark system theme.

v2.1.1 fixes expansion jumping across shared monitor edges and adds a muted charcoal rounded panel with a narrow pill tab. Docking retains its monitor, deliberate dragging can move across screens, and older saved positions remain compatible.

### New in v2.1: tray, edge docking and remembered sign-in

- Minimize and Close hide the window in the Windows notification tray by default, keeping refresh active. Click the tray icon to restore it; right-click for refresh, floating-window controls or **Quit application**. Disable the tray option for normal window behavior. Without an available tray, the app does not hide the window into an inaccessible state.
- An optional always-on-top floating window is shown by default. Drag its header to move; release near either side of the screen to dock. After the pointer leaves for about 0.8 seconds it becomes a small tab; hover to expand. `‹` docks and collapses immediately, `↗` opens the main window, and `×` hides only the floating window. Visibility and position are remembered. Stale and expired readings remain labeled.
- Startup checks the official Codex client's saved session before requesting sign-in; the login button disappears once connected. Certain expired-authentication failures get one official token-refresh attempt. Revoked/invalid authorization can still require sign-in. Minimizing, closing to tray and quitting do not log out. Claude Code manages its own saved login; waiting for activity is not a sign-out.
- Launching another instance restores the existing window. After changing language, **Quit application** from the tray before reopening.
- Exit the old application before installing the update over it. No uninstall, data deletion or sign-out is necessary. The data folder remains `AIUsageMonitorV2`.

### Features and limitations

| Integration | v2.2.0 support |
| --- | --- |
| Codex subscription quotas | Official App Server readings, every 60 seconds; manual refresh and multiple returned windows |
| Official Codex IDE extension | Usage billed to the same account/workspace subscription is reflected in account limits; do not add it again |
| Claude Code subscription quotas | Receives available five-hour, weekly and other quota fields from the official terminal `statusLine`; activity-driven |
| Claude Code graphical IDE panel | Usage counts toward applicable account limits, but **direct automatic synchronization from the graphical panel is not implemented** |
| ChatGPT Work | Shares usage with Codex according to official documentation; display follows returned windows |
| Ordinary ChatGPT chat / model message quotas | **Not integrated**; the Codex percentage does not describe all ChatGPT features |
| API-key billing, Gemini, multiple-account aggregation | Not integrated |
| Language, fees and history | English / Simplified Chinese installer; manual monthly fees; local CSV export |

Remaining percentage is `100 - reported used percentage`. The app does not infer subscription quotas from message/token counts or add different quota windows together.

### Install

Requires Windows 10 2004 (19041) or newer / Windows 11, x64.

1. If the maintainer publishes an installer under repository **Releases**, download `AIUsageMonitorSetup_v2.2.0.exe`. GitHub **Download ZIP** provides source only; otherwise use the source instructions below.
2. Run setup and select **English** or **简体中文**. Python is bundled; the default per-user installation does not require administrator rights.
3. Language changes take effect after quitting from the tray menu and reopening the app.
4. Install official Codex and/or Claude Code clients separately.

The current installer is unsigned. Verify its source and any supplied SHA-256 manifest. Do not disable system security protection to run it.

### Connect Codex

Install the [official Codex CLI](https://learn.chatgpt.com/docs/cli) or desktop app. Click **Sign in to Codex**, then authorize in the official browser page. If detection fails, select the official `codex.exe` manually. Refresh runs every 60 seconds or on request.

The app uses a separate `codex-home` profile without copying other applications' credentials. Use the same account and workspace as your IDE extension. API-key billing is separate and is not supported by this monitor.

### Connect Claude Code

**The current “Sign-in / usage guide” button displays instructions; it does not launch sign-in.**

1. Install the latest client using the [official quickstart](https://code.claude.com/docs/en/quickstart).
2. Run `claude auth login --claudeai` in PowerShell and complete browser authorization. Alternatively, start `claude` and use `/login`.
3. Click **Enable usage connection** in the monitor.
4. Start or reopen an interactive Claude Code **terminal session**, finish onboarding, and send a normal message. Wait for its response.
5. The monitor checks the local observation file about every five seconds; it does not poll Claude's account service every five seconds.

If `claude` is not recognized, reopen your terminal. For an existing native installation in the default location, these commands bypass PATH lookup:

```powershell
& "$env:USERPROFILE\.local\bin\claude.exe" auth login --claudeai
& "$env:USERPROFILE\.local\bin\claude.exe"
```

The first signs in; the second starts a conversation. If the file does not exist, complete the official installation first.

**IDE users:** run Claude Code in VS Code's integrated terminal or enable **Use Terminal** in the extension settings to use this monitor's current feed. In the graphical extension panel, use `/usage` to view official limits. Do not assume an older monitor observation is live.

Claude web, desktop and Claude Code usage under the same subscription affects shared limits. A refreshed status-line quota is an account observation; the session dollar estimate describes only the reporting session.

The connection configures user-level `statusLine`. Replacing a custom status line requires confirmation and saves recovery information. Project or organization settings, or a different `CLAUDE_CONFIG_DIR`, can override the feed. Disconnecting or uninstalling attempts restoration; later user edits and the original backup are preserved.

### Interpret data and troubleshoot

- Missing fields stay unknown, not zero. Claude quota fields require a compatible client/account and typically appear after the first model response.
- Observations older than five minutes are marked stale. Reset time does not invent a fresh zero reading.
- Codex shows only returned windows; a missing five-hour window is not necessarily an error.
- Claude shows the latest local reporting session, with no multi-account isolation or aggregation. Wait for new data after changing accounts.
- Claude session cost is an estimate, **not an invoice or subscription charge**. Monthly fees are manual, without currency conversion; record shared plans once.
- Refreshing does not send model requests automatically. Messages you send to test the connection still count under provider rules.

| Symptom | Check |
| --- | --- |
| Waiting for Claude data | Sign-in alone is insufficient. Enable the feed, finish terminal onboarding and wait for a reply; the graphical panel is not directly connected |
| Claude data stops updating | Check timestamp, account, WSL/remote environment, configuration directory and overriding settings |
| Data arrives without quota | Update the client and check `/usage`; the provider may not supply these fields |
| Codex missing / offline | Check the official executable, network and sign-in; select `codex.exe` manually |
| Monthly fee differs from estimate | These are separate metrics; neither is a live invoice feed |
| The app still runs after closing | Close hides to tray by default and refresh continues. Choose Quit application to stop it. The Claude helper can still write observations independently; disconnect it in the app |

### Privacy and uninstall

Data lives in `%LOCALAPPDATA%\AIUsageMonitorV2`: settings, 90-day usage history, the latest Claude observation, status-line recovery information and a separate official Codex sign-in profile.

The Claude helper retains only quota fields, reset/observation times and session cost estimates, not raw input, conversations or session IDs. **Never publish the runtime folder:** profiles may contain credentials, recovery records/logs may include local paths, and CSV files disclose usage history. See [SECURITY.md](SECURITY.md). The app has no custom analytics service; official clients still perform their own authentication and network requests.

Uninstall through Windows **Settings → Apps → Installed apps → AI Usage Monitor v2**. Program files are removed and Claude restoration is attempted, but **history and the separate Codex sign-in remain**. For full removal, sign out and disconnect in the app, uninstall, then manually delete the data directory. v1 data is unaffected.

### Run and build from source

Use Windows x64 and Python 3.12. From the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Install [Inno Setup 6.5+](https://jrsoftware.org/isinfo.php), then supply your actual compiler path:

```powershell
.\.venv\Scripts\python.exe build.py --iscc "C:\path\to\ISCC.exe"
```

Alternatively, `build_exe.bat --iscc "C:\path\to\ISCC.exe"` creates the environment and builds using the default Python 3; confirm its version first. Generated `work` and `outputs` folders are in the **parent of the project folder**. A frozen app requires its complete dependency folder; use the installer for distribution.

For isolated tests, set `AI_USAGE_MONITOR_DATA` to a temporary folder. If testing Claude settings changes, also set `CLAUDE_CONFIG_DIR` to a separate test directory. `--demo --smoke-test --lang en --snapshot preview.png` uses labeled demonstration data without connecting to real accounts.

### Publish on GitHub

Use the directory containing `README.md`, `app.py` and `LICENSE` as your repository root. Upload the prepared source contents, not the outer working directory, runtime data, Python caches or unrelated projects.

Create an empty repository, upload reviewed source, inspect the file list, then optionally create a Release with separately reviewed binaries and hashes. Review screenshots, logs, CSV files and Git history before publishing. `.gitignore` does not remove secrets already committed. See [SHARING_AUDIT.md](SHARING_AUDIT.md).

Project-owned code is licensed under [MIT](LICENSE). Qt, Python and other dependencies retain their own licenses and distribution requirements; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Official references / 官方参考

- [Codex App Server](https://learn.chatgpt.com/docs/app-server)
- [Codex and ChatGPT Work usage](https://learn.chatgpt.com/docs/pricing)
- [Claude Code status-line data](https://code.claude.com/docs/en/statusline)
- [Claude Code in VS Code](https://code.claude.com/docs/en/vs-code)
- [Claude shared usage limits](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work)
- [Claude Code settings](https://code.claude.com/docs/en/settings)

## Documentation references / 项目说明参考

文档组织参考了 [PowerToys](https://github.com/microsoft/PowerToys) 的安装、参与和许可证入口，以及 [ShareX](https://github.com/ShareX/ShareX) 对免费开源定位与功能的清晰介绍。仅借鉴组织方式，没有复制其代码、Logo 或产品图片；不表示这些项目为本项目背书。

The documentation structure takes inspiration from [PowerToys](https://github.com/microsoft/PowerToys) for installation, contribution and license navigation, and [ShareX](https://github.com/ShareX/ShareX) for its clear free/open-source positioning and feature overview. No code, logos or product images were copied, and no endorsement is implied.
