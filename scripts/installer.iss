[Setup]
AppId={{9F82A4D1-5C82-4B6A-914B-E0E9B0F1C312}
AppName=Anamnesix
AppVersion=1.1.4
AppPublisher=Anamnesix Health Technologies
AppPublisherURL=https://github.com/AprileNunzio/Anamnesix
AppSupportURL=https://github.com/AprileNunzio/Anamnesix
AppUpdatesURL=https://github.com/AprileNunzio/Anamnesix
DefaultDirName={autopf}\Anamnesix
DisableProgramGroupPage=yes
OutputBaseFilename=Anamnesix_Setup
OutputDir=..\Output
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=yes

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\Anamnesix.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\frontend\*"; DestDir: "{userdocs}\Anamnesix\frontend"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Anamnesix"; Filename: "{app}\Anamnesix.exe"
Name: "{autodesktop}\Anamnesix"; Filename: "{app}\Anamnesix.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Anamnesix.exe"; Description: "{cm:LaunchProgram,Anamnesix}"; Flags: nowait postinstall skipifsilent
