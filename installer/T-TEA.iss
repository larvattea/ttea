; Instalador do T-TEA (Inno Setup 6). Normalmente compilado pelo build.ps1,
; que passa a versão e a pasta do build:
;   ISCC.exe /DAppVersion=1.4.1 /DAppDir=..\build\dist\T-TEA installer\T-TEA.iss

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef AppDir
  #define AppDir "..\build\dist\T-TEA"
#endif

[Setup]
; Não mudar o AppId: é ele que faz uma versão nova atualizar a instalação
; existente em vez de instalar outra cópia.
AppId={{6C1B7E2A-3F4D-4B8E-9A51-2D7C0E9F4A13}
AppName=T-TEA
AppVersion={#AppVersion}
AppVerName=T-TEA {#AppVersion}
AppPublisher=UDESC - Laboratório LARVA
AppPublisherURL=https://github.com/larvattea
; Instala por usuário (sem pedir administrador): os jogos gravam jogadores,
; calibração e configurações dentro da própria pasta do programa, e ela
; precisa ser gravável. Em "Arquivos de Programas" não seria.
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\T-TEA
DefaultGroupName=T-TEA
DisableProgramGroupPage=yes
; mediapipe só existe para 64 bits; Windows 10 ou mais novo.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
SetupIconFile=ttea.ico
UninstallDisplayIcon={app}\T-TEA.exe
OutputDir=..\build
OutputBaseFilename=T-TEA-{#AppVersion}-setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes

[Languages]
Name: "ptbr"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Dirs]
Name: "{app}\Jogadores"; Flags: uninsneveruninstall

[Files]
; Programa e recursos: sempre substituídos na atualização.
Source: "{#AppDir}\*"; DestDir: "{app}"; Excludes: "\Jogadores\*"; Flags: ignoreversion recursesubdirs createallsubdirs
; Jogadores de exemplo: só entram se ainda não existirem, e nunca são
; apagados - é onde ficam os cadastros e o histórico das sessões.
Source: "{#AppDir}\Jogadores\*"; DestDir: "{app}\Jogadores"; Flags: onlyifdoesntexist uninsneveruninstall skipifsourcedoesntexist
; calibracao.csv, config.json e os logs são criados pelo próprio programa e
; não fazem parte da instalação: sobrevivem a atualizações e à desinstalação.

[Icons]
Name: "{group}\T-TEA"; Filename: "{app}\T-TEA.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\T-TEA"; Filename: "{app}\T-TEA.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\T-TEA.exe"; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,T-TEA}"; Flags: nowait postinstall skipifsilent
