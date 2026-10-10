# GitHub sharing review / GitHub 分享检查记录

## Reviewed source upload / 本次源码上传复核（2026-10-10）

- 对当前源码及最终 ZIP 检查个人用户名/路径、常见 API Key、访问令牌、JWT、私钥、邮箱及可疑运行文件；不把匹配到的私密原文写入公开报告。可发布源码未发现用户个人资料或实际凭据。邮箱命中是原始译者及 Python 许可公开署名，保留。
- 本地 Python 缓存确实含开发机绝对路径；最终包用明确清单导出，排除所有缓存、账号、日志、数据库、CSV、真实截图和 .git。不要直接上传整个工作目录。
- 本次附独立中英文 README、免费/MIT说明、上传指南和字体许可检查，保留 Inno Setup 原始许可。源码包不含字体、EXE、DLL 或 Qt 编译翻译；不将旧安装包作为附件。
- 现有构建目录及可解包 Python 内容也进行了特征扫描。此类扫描会命中第三方构建路径、解析器标记和压缩数据，不能当作全面的二进制凭据或许可认证；当前交付结论仅限所列源码包。
- 旧构建发现未使用的商业/GPLv3 Qt Virtual Keyboard 依赖；源码构建流程已排除，二进制对应源码及完整告知义务见 LICENSE_REVIEW.md。早期报告不能覆盖此项新发现。
- 最终 ZIP 解压后运行 36 项核心/协议/提醒测试及 14 项桌面测试，并验证文件清单、CRC 和 SHA-256。当前外层仓库无提交；本包不含任何 Git 历史。此项为源码包准备阶段记录；随后发布沿用目标仓库的既有历史。

The source and final ZIP were checked for owner identifiers/paths, common API keys and access tokens, JWTs, private keys, email addresses and runtime artifacts, without publishing sensitive match contents. No personal user information or actual credentials were found in the reviewed source. Email matches are preserved upstream translator/Python attribution. Local Python caches contain development-machine paths and are excluded by the export allowlist, together with accounts, logs, databases, CSVs, real screenshots and Git history.

The delivery adds separate Chinese/English READMEs, free/MIT positioning, upload instructions, font/license review and the original Inno Setup license. It contains no fonts, executables, DLLs or compiled Qt translations. Broader build scans are not a full binary or legal certification. The unused commercial/GPLv3 Qt Virtual Keyboard found in the older build is now excluded by the source build process; remaining binary source/notice obligations are recorded in LICENSE_REVIEW.md. Earlier review entries do not resolve this new finding.

The extracted final archive passes 36 core/protocol/alert and 14 desktop tests, file-list/CRC checks and SHA-256 verification. The outer repository has no commits; no Git history is included and this describes the archive-preparation stage; repository publication retains the target repository history. Findings apply to this archive, not to future edits or every possible secret format.


## v2.2.0 addendum / v2.2.0 补充（2026-10-10）

增加菜单配色及额度提醒，提醒记录仅包含平台、额度窗口、周期时间和已提醒档位，存入被忽略的本地 settings.json。源码分享包增加 test_alerts.py，继续按文件白名单导出及扫描个人路径和常见凭据特征；不含真实账号数据。50 项自动测试通过。本记录不代表全面二进制审计。

Added menu colors and quota alerts. Deduplication stores only provider/window names, cycle timestamps and alert thresholds in the ignored local settings.json. The source allowlist adds test_alerts.py; personal-path and common-credential scans remain required and real account data is excluded. All 50 automated tests pass. This is not a comprehensive binary audit.

## v2.1.1 addendum / v2.1.1 补充（2026-10-10）

v2.1.1 修复多屏定位并调整悬浮窗外观。源码包继续按明确文件清单导出，排除账号及运行数据，并检查个人路径和常见凭据特征。记录屏幕名称和几何位置，不读取硬件序列号。25 项核心测试和 12 项桌面测试通过。本补充不是对第三方二进制的全面安全审计。

v2.1.1 fixes monitor anchoring and restyles the floating window. The source archive retains an explicit file allowlist, excludes account/runtime data and checks personal paths and common credential patterns. Position preferences store monitor names and geometry, without reading hardware serial numbers. All 25 core and 12 desktop tests pass. This addendum is not a comprehensive audit of third-party binaries.

## v2.1 addendum / v2.1 补充（2026-10-10）

新的 `AIUsageMonitorDesktop_v2.1_GitHub.zip` 加入 `desktop.py`、桌面交互测试和 CHANGELOG；沿用明确文件清单导出，排除账号、缓存、日志和运行数据，并重新检查个人路径与凭据特征。25 项核心测试与 6 项桌面测试通过。下文是 v2.0 初次检查的历史记录，不应理解为新增二进制文件的全面审计。

The v2.1 source package adds `desktop.py`, desktop interaction tests and CHANGELOG. Export uses an explicit file list, excluding account data, caches, logs and runtime files, with renewed personal-path and credential-pattern checks. All 25 core tests and 6 desktop tests pass. The original v2.0 review below is historical and is not a comprehensive audit of new binaries.

Review date / 检查日期：2026-10-09  
Application / 应用版本：2.0.0  
Delivery / 交付：`AIUsageMonitorDesktop_v2_GitHub.zip`（源码 / source only）

## 中文

### 结论

在整理后的源码分享包中，未发现实际账号凭据、API 密钥、个人邮箱、本机用户名或个人绝对路径。该结论针对本次检查的文件，不代表对未知秘密、未来修改或所有软件漏洞的保证。

### 发现与处理

| 项目 | 检查结果与处理 |
| --- | --- |
| Python 缓存 | 工作源码目录内的部分 `.pyc` 含本机绝对路径；分享包全部排除 `__pycache__` 和字节码，原有源码 ZIP 也已排除 |
| 外层工作目录 | 含本机脚本、测试资料及无关项目；不属于分享范围，只导出本项目的明确文件清单 |
| 凭据与运行数据 | 分享包不包含 `.codex`、`.claude`、`codex-home`、`auth.json`、数据库、CSV、日志或状态栏恢复记录 |
| API Key / Token / 私钥 | 对源码、原有 ZIP、构建目录及可读取的压缩 Python 代码进行了特征扫描；未发现实际用户密钥。依赖中的语言代码、解析标记等命中经复核为误报 |
| 第三方邮箱与路径 | 翻译、许可证、标准库与二进制依赖中含公开上游署名、示例和上游编译路径；并非本机用户数据，必要许可声明保留 |
| 截图 | 新源码分享包不附任何截图，也不附用户提供的真实账号截图 |
| Git 历史 | 检查时外层仓库尚无提交；分享包不含 `.git`，应在新仓库根目录上传整理后的内容 |
| 忽略规则 | 补充凭据、缓存、虚拟环境、生成文件、运行数据和导出文件规则；忽略规则不能清除已经提交的内容 |
| 文档及许可证 | 新增完整中英文使用说明、安全分享说明和 MIT 许可证；后续构建会携带 LICENSE 和 SECURITY.md |

### 检查范围与限制

- 检查项目源文件、原有源码/完整 ZIP 成员，以及现有 Windows 构建目录中的文件；解读两个应用 EXE 的 PyInstaller 压缩 Python 内容。
- 检查常见提供商密钥格式、JWT、私钥标记、邮箱、本机身份路径和不应公开的文件类型；结合代码审阅区分示例、上游信息和真实秘密。
- 原安装器的压缩数据未作为独立安装镜像完整重建审计；对二进制的扫描不等同于恶意软件检测或依赖供应链审计。新分享包仅含源码，不重新发布旧 EXE。
- 最终源码 ZIP 经 CRC 校验、文件白名单检查、个人路径/凭据特征复查及相对文档链接检查。项目已有 20 项测试在解压后的源码上重新运行通过。
- 本次没有创建 GitHub 仓库或推送内容，没有访问或导出实际凭据。后续上传、发布 Release 或添加新文件时应重新检查。

### 上传建议

解压源码包，将其中 `README.md` 所在文件夹的内容上传为仓库根目录，保留 `.gitignore`、`LICENSE`、第三方说明及许可文件。不要将整个开发工作目录上传。若之后发布安装器，应从这份源码重新构建并检查产物、许可证、截图和日志。

## English

### Result

No actual account credentials, API keys, personal email addresses, local owner name or personal absolute paths were found in the prepared source package. This is a review of the inspected files, not a guarantee against unknown secrets, future changes or all software vulnerabilities.

### Findings and remediation

| Item | Result / action |
| --- | --- |
| Python caches | Some development `.pyc` files contained local absolute paths. All bytecode and `__pycache__` folders are excluded; the previous source ZIP already excluded them |
| Outer working directory | Contains machine-specific scripts, test artifacts and unrelated work; only an explicit project file list is exported |
| Credentials and runtime data | No client profiles, `codex-home`, `auth.json`, databases, CSV exports, logs or status-line recovery data are included |
| Key / token / private-key scan | Source, previous archives, staged binaries and readable compressed Python code were scanned; no actual user keys found. Dependency locale strings and parsing markers were reviewed as false positives |
| Third-party attribution | Public upstream contacts, examples and upstream build paths exist in translation/license/runtime files; necessary notices are retained |
| Screenshots | No screenshots are included in the new source package, including the user's real-account screenshot |
| Git history | The outer repository had no commits at review time; no `.git` directory is included |
| Ignore rules | Expanded to cover profiles, caches, virtual environments, builds, runtime data and exports; this does not clean prior commits |
| Documentation and licensing | Added bilingual instructions, safe-sharing documentation and MIT licensing; future builds include LICENSE and SECURITY.md |

### Scope and limits

- Reviewed project sources, members of previous source/full ZIPs and the existing Windows build tree, including compressed Python content in both PyInstaller executables.
- Checked common provider-key/JWT patterns, private-key markers, email addresses, local identity paths and unwanted file types. Reviewed matches to distinguish examples and upstream content from secrets.
- The original installer's compressed payload was not independently reconstructed as a complete install image for this review. Binary string scanning is not malware detection or a dependency supply-chain audit. The new package is source only; old executables are not republished.
- The final ZIP passed CRC, explicit-file-list, personal-path/credential-pattern and relative-document-link checks. All 20 existing tests passed from the extracted source.
- No GitHub repository was created or pushed, and no real credentials were accessed or exported. Recheck future commits and release assets.

### Upload guidance

Extract the package and upload the contents of the folder containing `README.md` as the repository root. Keep `.gitignore`, `LICENSE`, third-party notices and license texts. Do not upload the whole development workspace. Rebuild future installers from this reviewed source and review the resulting binaries, notices, screenshots and logs before release.

## Repository publication / 仓库发布

发布内容来自上述审核包（33 个文件），仅更新了上传阶段的文档措辞。保留目标仓库初始化历史，不声称旧历史匿名。新提交使用项目署名及 GitHub noreply 邮箱，未上传运行数据或安装器。

Publication uses the reviewed 33-file archive with documentation wording updated for publication. The target repository's initial history is retained and is not claimed to be anonymous. The new commit uses project attribution and a GitHub noreply email; runtime data and installers are excluded.
