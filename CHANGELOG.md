# Changes / 更新记录

## 2.2.1 — 2026-10-10

发布 Windows 安装器，精简无用 Qt 模块，补齐依赖源码、许可告知和中英文直接下载说明。功能与 v2.2.0 相同。

Publishes a Windows installer with a reduced Qt module set, corresponding dependency sources, preserved notices and bilingual direct-download instructions. Application features are unchanged from v2.2.0.

## 2.2.0 — 2026-10-10

- 中文：修复托盘右键菜单在深色主题下继承深色文字导致的低对比度，菜单及勾选状态有独立配色。新增默认开启的剩余额度 50% / 20% / 10% 通知；按平台、额度窗口和周期去重，重启保留。包括返回的 5 小时和周额度，无套餐名称限制。一次跨多档只提示最紧急档，旧数据和未知额度不提醒。主窗口和托盘均可开关；系统勿扰可能抑制通知。Claude 仍依赖终端状态栏活动。
- English: Fixed poor tray-menu contrast caused by inherited dark text on a dark native menu. Added enabled-by-default notifications at 50% / 20% / 10% remaining, deduplicated by provider, window and cycle across restarts. Returned five-hour and weekly windows are supported without plan filtering. Crossing multiple thresholds sends only the most urgent alert; stale or unknown data does not notify. Toggle alerts in the main window or tray. System Do Not Disturb can suppress notifications; Claude still depends on terminal status-line activity.
- 验证 / Validation: 36 core/protocol/alert tests + 14 desktop tests, including thresholds, skipped thresholds, restart persistence, cycle resets, independent windows, notification dispatch/toggle and demo suppression; bilingual isolated installation and upgrade checks.
- 更新 / Update: fully quit from the tray, then install `AIUsageMonitorSetup_v2.2.0.exe` over the old version. 从托盘完全退出旧版后覆盖安装，保留登录及设置。

## 2.1.1 — 2026-10-10

### 中文

- 修复双显示器交界处悬浮窗展开后跳到另一块屏幕的问题：吸附时固定所属屏幕，收起、展开和重启均保留该屏幕；仍可主动拖到另一块屏幕。
- 兼容旧版保存的位置；显示器断开或布局改变时重新确保窗口可见。
- 悬浮面板改为柔和的深灰配色与圆角，贴边标签缩为半透明的窄胶囊，减少亮白色干扰。

更新：先从托盘菜单完全退出旧程序，再运行 `AIUsageMonitorSetup_v2.1.1.exe` 覆盖安装，保留原有设置和登录数据。

验证：25 项核心测试、12 项桌面测试，包含模拟双屏交界反复展开、负坐标屏幕、跨屏拖动、屏幕断开及新旧位置恢复。发布前另执行中英文隔离安装、覆盖更新和卸载检查。预览使用演示数据。

### English

- Fixed floating windows jumping to another monitor when expanded at a shared edge. Docking now retains its monitor through collapse, expansion and restart; deliberate dragging can still move it to another screen.
- Preserved compatibility with older saved positions and kept windows visible after monitor removal or layout changes.
- Restyled the panel with muted charcoal colors and rounded corners. The edge tab is now a narrow translucent pill instead of a bright white badge.

Update: fully quit the old app from its tray menu, then install `AIUsageMonitorSetup_v2.1.1.exe` over it. Existing settings and sign-in data are retained.

Validation: 25 core tests and 12 desktop tests, including simulated shared monitor edges, repeated expansion, negative screen coordinates, cross-screen dragging, monitor removal and old/new position restoration. Release checks also cover isolated bilingual installation, in-place updates and uninstall. Previews use synthetic data.

## 2.1.0 — 2026-10-10

### 中文

- 新增系统托盘：最小化、关闭时默认隐藏到托盘，继续更新用量。右键可恢复窗口、刷新、切换悬浮窗或完全退出；可关闭该偏好。
- 新增置顶悬浮窗：拖动标题栏移动，贴屏幕左右边缘自动吸附收起，移入展开；保留显示偏好与位置，并标记旧数据。
- 启动先检查已保存的官方 Codex 登录，不因启动时点击登录而重复打开授权页；已连接时隐藏登录按钮。
- 部分认证过期错误会尝试一次官方令牌续期；失效或撤销的授权仍需用户重新登录。
- 修复手动选择的 Codex 路径因客户端更新失效时不能重新查找的问题。
- 再次运行快捷方式会恢复已经打开的窗口，避免多开。
- 保留原数据目录及安装标识，支持覆盖更新。关闭或退出程序不会主动退出账号。

更新方式：先完全退出旧程序，再运行 `AIUsageMonitorSetup_v2.1.0.exe` 覆盖安装。不必卸载、删除数据或退出账号。新版默认关闭到托盘；要结束程序，请在托盘菜单选择“退出程序”。Claude 的 IDE 图形面板自动同步限制未改变。

验证：25 项额度/协议/存储测试、6 项桌面交互测试；双语冻结程序启动及托盘/悬浮窗检查；隔离安装与覆盖安装状态保留、卸载恢复检查。使用现有官方登录连续建立两次 Codex 连接，均无需打开登录页面。所有演示截图只使用合成数据。

### English

- Added a notification-tray icon. Minimize and Close hide to tray and keep refreshing by default. The menu restores the window, refreshes, toggles the floating window or quits; the tray preference can be disabled.
- Added an always-on-top floating window with dragging, left/right edge docking, auto-collapse and hover expansion. Visibility and position persist; stale readings stay labeled.
- Startup checks saved official Codex authentication before starting browser login, including sign-in clicks during startup. The login button is hidden while connected.
- Certain expired-authentication errors get one official token-refresh attempt. Invalid or revoked authorization still requires user sign-in.
- Rediscovers Codex when an explicitly selected executable disappears after a client update.
- A second launch restores the existing window instead of opening another instance.
- Preserves the application data folder and installation identity for in-place updates. Closing/quitting does not sign the user out.

Update: fully exit the old app and install `AIUsageMonitorSetup_v2.1.0.exe` over it. No uninstall, data deletion or sign-out is needed. To exit the new version, use **Quit application** in the tray menu. Claude graphical IDE-panel synchronization limitations are unchanged.

Validation: 25 quota/protocol/storage tests and 6 desktop interaction tests; bilingual frozen-app startup and tray/floating checks; isolated install, install-over-existing state preservation and uninstall restoration. Two successive real Codex connections reused existing official authentication without opening a login page. All preview screenshots use synthetic data.
