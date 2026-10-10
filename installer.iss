#ifndef AppDist
  #define AppDist "..\work\v2-dist\AIUsageMonitor"
#endif
#ifndef OutputPath
  #define OutputPath "..\outputs"
#endif

[Setup]
#ifdef QATest
AppId=AIUsageMonitor-QA-v21
DefaultGroupName=AI Usage Monitor QA
#else
AppId={{AFD3868E-F422-4CAA-9598-CDF8CF60C2BA}
DefaultGroupName=AI Usage Monitor v2
#endif
AppName=AI Usage Monitor v2
AppVersion=2.2.0
AppVerName=AI Usage Monitor 2.2.0
DefaultDirName={localappdata}\Programs\AIUsageMonitorV2
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19041
OutputDir={#OutputPath}
OutputBaseFilename=AIUsageMonitorSetup_v2.2.0
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\AIUsageMonitor.exe
#ifdef QATest
AppMutex=AIUsageMonitor-QA-v21
#else
AppMutex=AIUsageMonitorV2
#endif
WizardStyle=modern
ShowLanguageDialog=yes
UsePreviousLanguage=no
DisableProgramGroupPage=yes
Compression=lzma2/fast
SolidCompression=yes
CloseApplications=no
VersionInfoVersion=2.2.0.0
VersionInfoDescription=AI Usage Monitor bilingual setup

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"; InfoBeforeFile: "assets\install-en.txt"
Name: "zh"; MessagesFile: "assets\ChineseSimplified.isl"; InfoBeforeFile: "assets\install-zh.txt"

[CustomMessages]
en.DesktopShortcut=Create a desktop shortcut
zh.DesktopShortcut=创建桌面快捷方式
en.LaunchApp=Launch AI Usage Monitor
zh.LaunchApp=启动 AI 用量监控

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; Flags: unchecked

[Files]
Source: "{#AppDist}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; Remove only obsolete DLLs from older builds of this application.
Type: files; Name: "{app}\_internal\icuuc.dll"
Type: files; Name: "{app}\_internal\icudt78.dll"

[Icons]
Name: "{group}\AI Usage Monitor v2"; Filename: "{app}\AIUsageMonitor.exe"
Name: "{autodesktop}\AI Usage Monitor v2"; Filename: "{app}\AIUsageMonitor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AIUsageMonitor.exe"; Parameters: "--set-language {language}"; Flags: runhidden waituntilterminated
Filename: "{app}\AIUsageMonitor.exe"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\AIUsageMonitor.exe"; Parameters: "--disconnect-claude"; Flags: runhidden waituntilterminated; RunOnceId: "RestoreClaudeStatusLine"
