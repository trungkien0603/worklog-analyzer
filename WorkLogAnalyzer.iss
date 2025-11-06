; ============================================
; WorkLogAnalyzer.iss
; Inno Setup 6.5+ — Windows x64, per-user install
; ============================================

; ---------- Thông tin ứng dụng ----------
#define MyAppName        "WorkLogAnalyzer"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "Your Company"
#define MyAppURL         "https://example.com"
#define MyAppExeName     "WorkLogAnalyzer.exe"
; Tạo GUID riêng cho app (Tools > Generate GUID trong Inno Setup)
#define MyAppID          "{1E2F3C7B-2C44-4A7B-9A62-9A7A9C2B9D83}"

; (Tùy chọn) Icon cho bộ cài: chỉ set nếu có file .ico
; Đặt file app.ico cùng thư mục .iss hoặc sửa đường dẫn bên dưới
#define AppIcoPath "app.ico"

; ============================================
[Setup]
; Nhận diện & hiển thị
AppId={{#MyAppID}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
UninstallDisplayIcon={app}\{#MyAppExeName}
#ifdef AppIcoPath
#ifexist AppIcoPath
SetupIconFile={#AppIcoPath}
#endif
#endif

; Vị trí cài đặt (per-user, không cần quyền admin)
DefaultDirName={userpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UsePreviousAppDir=yes
UsePreviousLanguage=yes
AllowNoIcons=yes

; Đầu ra
OutputDir=Output
OutputBaseFilename=Setup_{#MyAppName}_x64

; Nén & giao diện
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupLogging=yes

; Kiến trúc & quyền
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0.18362

; Trải nghiệm cài đặt
DisableDirPage=no
DisableProgramGroupPage=no
CloseApplications=yes
RestartApplications=no
RestartIfNeededByRun=yes
DirExistsWarning=no

; Ngăn cài đè khi app đang chạy
AppMutex={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional tasks:"; Flags: unchecked

; ============================================
; Sao chép file
; ============================================
[Files]
; Ưu tiên bản release nếu có
#ifexist "dist\WorkLogAnalyzer.exe"
Source: "dist\WorkLogAnalyzer.exe"; DestDir: "{app}"; Flags: ignoreversion
#endif

; Fallback: dùng bản debug và đổi tên thành EXE chuẩn nếu thiếu bản release
#ifexist "dist\WorkLogAnalyzer_dbg.exe"
#ifnexist "dist\WorkLogAnalyzer.exe"
Source: "dist\WorkLogAnalyzer_dbg.exe"; DestDir: "{app}"; DestName: "WorkLogAnalyzer.exe"; Flags: ignoreversion
#endif
#endif

; Copy thư mục fonts nếu có
#ifexist "fonts"
Source: "fonts\*"; DestDir: "{app}\fonts"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

; ============================================
; Shortcut
; ============================================
[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
; Desktop (theo task)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; ============================================
; Chạy app sau khi cài
; ============================================
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

; ============================================
; Registry: App Paths (per-user)
; Cho phép chạy 'WorkLogAnalyzer' từ Win+R / Command Prompt
; ============================================
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; \
    ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; \
    ValueType: string; ValueName: "Path"; ValueData: "{app}"; Flags: uninsdeletevalue

; ============================================
; (Tùy chọn) Ký số file cài đặt nếu bạn có tool ký
; Bỏ comment và điền lệnh ký phù hợp.
; ============================================
;[SignTool]
;SignTool=your-signtool-command "$f"
