# AI Usage Monitor v2.2.0

[简体中文](README.zh-CN.md) · [Bilingual home](README.md)

**Free and open source — welcome!** Project-owned code uses [MIT](LICENSE); AI provider charges are separate.


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
