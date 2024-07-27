; NSIS Modern User Interface
; Template used: Basic Example Script by Joost Verburg

;--------------------------------
; Include Modern UI
!include "MUI2.nsh"

; To use WordFind
!include "WordFunc.nsh"

; To use GetSize
!include "FileFunc.nsh"

;--------------------------------
; General

!define NAME "GenshinRichPresence"
!define VERSION "1.1.0"

!define PROJECT_FOLDER ".\dist\${NAME}"
!define FILES_FOLDER "${PROJECT_FOLDER}"

!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}"
!define DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${NAME}.exe"

Name "${NAME}"
OutFile "${NAME}_v${VERSION}_Setup.exe"
Unicode True

; Get installation folder from registry if available
InstallDirRegKey HKCU "${DIR_REGKEY}" ""

; Default installation folder
InstallDir "$LOCALAPPDATA\${NAME}"

; Request application privileges for Windows Vista
RequestExecutionLevel user

; Show details: Expand "Show more" button
ShowInstDetails show
ShowUninstDetails show

BrandingText "NSIS"

;--------------------------------
; Interface Settings

!define MUI_ABORTWARNING

;--------------------------------
; Language Selection Dialog Settings

; Remember the installer language
; !define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
; !define MUI_LANGDLL_REGISTRY_KEY "Software\${NAME}"
; !define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

; Show all languages, despite user's codepage
!define MUI_LANGDLL_ALLLANGUAGES

;--------------------------------
; Pages

; Installer pages

; Welcome page
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE preSetup
!define MUI_WELCOMEPAGE_TITLE_3LINES
!define MUI_WELCOMEPAGE_TEXT "This setup will guide you through the installation of ${NAME}.$\n$\n\
    It will also help you to configure the 'config.ini' file. You can also check it out if you want to \
    customize or change a configuration later.$\n$\n\
    This is a FREE AND OPEN SOURCE SOFTWARE, if you have paid for it, you have been scammed.$\n$\n\
    This software is licensed under the MIT License. See the license for details.$\n$\n\
    Click Next to continue."
!insertmacro MUI_PAGE_WELCOME

; License page
; !insertmacro MUI_PAGE_LICENSE "${PROJECT_FOLDER}\LICENSE.rtf"

; !insertmacro MUI_PAGE_STARTMENU 0 $StartMenuFolder

; Request install directory page
!insertmacro MUI_PAGE_DIRECTORY

; Component checkboxes page
!insertmacro MUI_PAGE_COMPONENTS

; Custom GIMI directory page
Page custom pageGetGimiDir

; Custom game directory page
Page custom pageGetGameDir

; File installation page
; !define MUI_FINISHPAGE_NOAUTOCLOSE
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\${NAME}.exe"
!define MUI_FINISHPAGE_SHOWREADME "https://github.com/Artprozew/GenshinRichPresence/blob/master/LICENSE"
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Read LICENSE"
!insertmacro MUI_PAGE_FINISH


; Uninstaller pages

; Welcome page, uninstall location and finish
!define MUI_WELCOMEPAGE_TITLE_3LINES
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English" ; The first language is the default language
!insertmacro MUI_LANGUAGE "TradChinese" ; Used to set the game executable as YuanShen.exe

LangString gameExecutable ${LANG_ENGLISH} "GenshinImpact.exe"
LangString gameExecutable ${LANG_TRADCHINESE} "YuanShen.exe"

; Ask language on installer/uninstaller init
Function .onInit
    !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

; Function un.onInit
;     !insertmacro MUI_LANGDLL_DISPLAY
; FunctionEnd

;--------------------------------
; Pre-Setup functions

Function preSetup
    Var /GLOBAL gimiDir
    Var /GLOBAL gimiDirectoryText
    Var /GLOBAL gimiBrowseButton
    ; Default location
    StrCpy $gimiDir "C:\Downloads\3dmigoto\3DMigoto Loader.exe"

    Var /GLOBAL gameDir
    Var /GLOBAL gameDirectoryText
    Var /GLOBAL gameBrowseButton
    ; Default location
    StrCpy $gameDir "C:\Program Files\Genshin Impact\Genshin Impact game\$(gameExecutable)"

    Var /GLOBAL startGameAndGimiCheck
    Var /GLOBAL startGameAndGimiCheckStatus
    ; Defaults as checked
    StrCpy $startGameAndGimiCheckStatus 1

    Var /GLOBAL parentHwnd
FunctionEnd


;--------------------------------
; Installer Sections

Section "Main files"
    SectionIn RO
    SetDetailsPrint both

    DetailPrint "Checking for existing config file..."

    ${If} ${FileExists} "$INSTDIR\config.ini"
        DetailPrint "Backing up config file"

        ${If} ${FileExists} "$INSTDIR\backup_config.ini"
            MessageBox MB_YESNOCANCEL|MB_ICONEXCLAMATION "Seems like there is already a backup'ed 'config.ini' file.$\n\
            It is recommended to run the program to apply the backup first, or you can save the 'backup_config.ini' yourself to apply it later.$\n$\n\
            Do you want to overwrite it with the new one?$\n\
            YOU MAY LOSE all settings on your old backup 'backup_config.ini' file if you proceed.$\n$\n\
            'Yes' overwrites your 'backup_config.ini'.$\n\
            'No' keeps your 'backup_config.ini', but may overwrite the current 'config.ini' without making a backup of it.$\n\
            'Cancel' aborts the installation." \
            IDYES overwrite IDNO continue

            ; No jumpto, cancel was clicked
            Abort "Aborting installation"
        ${EndIf}

        overwrite:
        CopyFiles "$INSTDIR\config.ini" "$INSTDIR\backup_config.ini"
    ${EndIf}

    continue:

    DetailPrint "Extracting files..."
    SetOutPath "$INSTDIR"
    SetOverwrite on

    Sleep 1000
    File /r "${FILES_FOLDER}\*"

    Sleep 1500
    DetailPrint "Finished extraction"

    DetailPrint "Configuring ini file"
    WriteINIStr "$INSTDIR\config.ini" "SETTINGS" "GIMI_DIRECTORY" "$gimiDir"
    ${If} $startGameAndGimiCheckStatus == 1
        WriteINIStr "$INSTDIR\config.ini" "SETTINGS" "START_GAME_AND_GIMI" "True"
        WriteINIStr "$INSTDIR\config.ini" "SETTINGS" "GAME_EXE_PATH" "$gameDir"
    ${EndIf}

    ${If} "$(gameExecutable)" == "YuanShen.exe"
        WriteINIStr "$INSTDIR\config.ini" "SETTINGS" "GAME_PROCESS_NAME" "YuanShen.exe"
    ${EndIf}

    DetailPrint "Configuration finished"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    Sleep 1000
SectionEnd


Section "Desktop shortcut" DesktopShortcut
    DetailPrint "Creating Desktop shortcut"

    CreateShortCut "$DESKTOP\${NAME}.lnk" "$INSTDIR\${NAME}.exe"
SectionEnd


Section "Start Menu shortcut" StartMenuShortcut
    DetailPrint "Creating Start Menu shortcuts"

    CreateDirectory "$SMPROGRAMS\${NAME}"
    CreateShortCut "$SMPROGRAMS\${NAME}\${NAME}.lnk" "$INSTDIR\${NAME}.exe"
    CreateShortCut "$SMPROGRAMS\${NAME}\Uninstall ${NAME}.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd


Section "Registry keys" ConfigRegistry
    DetailPrint "Writing to registry"

    WriteRegStr HKCU ${DIR_REGKEY} "$INSTDIR\${NAME}.exe"
    WriteRegStr HKCU ${UNINST_KEY} "DisplayName" "$(^Name)"
    WriteRegStr HKCU ${UNINST_KEY} "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKCU ${UNINST_KEY} "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
    WriteRegStr HKCU ${UNINST_KEY} "DisplayIcon" "$INSTDIR\${NAME}.exe"
    WriteRegStr HKCU ${UNINST_KEY} "DisplayVersion" "${VERSION}"
    WriteRegStr HKCU ${UNINST_KEY} "URLInfoAbout" "https://www.github.com/Artprozew"
    WriteRegStr HKCU ${UNINST_KEY} "Publisher" "Artprozew"

    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU ${UNINST_KEY} "EstimatedSize" "$0"

    DetailPrint "Done writing to registry"
    Sleep 1500
SectionEnd


; Uninstaller Section
Section "Uninstall"
    SetDetailsPrint both
    DetailPrint "Deleting files..."

    Delete "$DESKTOP\{NAME}.lnk"
    Delete "$SMPROGRAMS\${NAME}\${NAME}.lnk"
    Delete "$SMPROGRAMS\${NAME}\Uninstall ${NAME}.lnk"

    Delete "$INSTDIR\*.*"
    Delete "$INSTDIR\backup_config.ini"
    Delete "$INSTDIR\Uninstall.exe"

    Sleep 1500
    DetailPrint "Deleting directories..."

    ; Need to change the OutPath to delete the main program folder?
    SetOutPath "$PROGRAMFILES"
    RMDir /r /REBOOTOK "$INSTDIR"
    RMDir /r /REBOOTOK "$SMPROGRAMS\${NAME}"

    Sleep 1000
    DetailPrint "Deleting registry keys..."

    ; DeleteRegKey /ifempty HKCU "Software\${NAME}"
    DeleteRegKey HKCU "${DIR_REGKEY}"
    DeleteRegKey HKCU "${UNINST_KEY}"

    DetailPrint "Uninstall complete"
    Sleep 1500

    SetAutoClose true
SectionEnd

;--------------------------------
; Descriptions

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${DesktopShortcut} "Create a shortcut for the program on your Desktop."
    !insertmacro MUI_DESCRIPTION_TEXT ${StartMenuShortcut} "Create a shortcut for the program/uninstaller on your Start Menu."
    !insertmacro MUI_DESCRIPTION_TEXT ${ConfigRegistry} "Add the uninstaller and other useful configurations to the Windows registry.$\n\
        If unchecked, it will act like a standalone program."
!insertmacro MUI_FUNCTION_DESCRIPTION_END


;--------------------------------
; Macros

!macro checkFileName filePath fileName
    ${WordFind} "${filePath}" "\" "-1" $R0
    ${If} $R0 == "${fileName}"
        EnableWindow $parentHwnd 1
    ${Else}
        EnableWindow $parentHwnd 0
    ${EndIf}
!macroend

;--------------------------------
; Custom Pages

; Get GIMI directory page

Function pageGetGimiDir
    !insertmacro MUI_HEADER_TEXT "Choose 3DMigoto Location" \
        "Choose the 3DMigoto Loader executable destination."

    GetDlgItem $parentHwnd $HWNDPARENT 1

    nsDialogs::Create 1018
    Pop $0
    ${If} $0 == error
        Abort
    ${EndIf}

    ${NSD_CreateLabel} 0 0 100% 35u "Choose the destination to your '3DMigoto Loader.exe' executable file."
    Pop $0

    ${NSD_CreateText} 0 35u 75% 12u "$gimiDir"
    Pop $gimiDirectoryText
    ${NSD_OnChange} $gimiDirectoryText onGimiDirChange

    ${NSD_CreateBrowseButton} 80% 35u 20% 15u "Browse"
    Pop $gimiBrowseButton
    ${NSD_OnClick} $gimiBrowseButton onGimiBrowseButtonClick

    ; Run checks
    Call onGimiDirChange

    nsDialogs::Show
FunctionEnd


Function onGimiBrowseButtonClick
    nsDialogs::SelectFileDialog open "$gimiDir" ".exe files|*.exe"
    Pop $0

    ${If} $0 != error
    ${AndIf} $0 != ""
        StrCpy $gimiDir $0
        ${NSD_SetText} $gimiDirectoryText $gimiDir
    ${EndIf}
FunctionEnd


Function onGimiDirChange
    ${NSD_GetText} $gimiDirectoryText $gimiDir

    ${If} ${FileExists} "$gimiDir"
        !insertmacro checkFileName $gimiDir "3DMigoto Loader.exe"
    ${Else}
        EnableWindow $parentHwnd 0
    ${EndIf}
FunctionEnd


;--------------------------------
; Get game directory page

Function pageGetGameDir
    !insertmacro MUI_HEADER_TEXT "Choose Genshin Impact Location" \
        "Choose the Genshin Impact executable destination."

    GetDlgItem $parentHwnd $HWNDPARENT 1

    nsDialogs::Create 1018
    Pop $0
    ${If} $0 == error
        Abort
    ${EndIf}

    ${NSD_CreateLabel} 0 0 100% 35u "Choose the destination to your '$(gameExecutable)' executable file.$\n$\n\
        This is only required if you check the checkbox below, and will only be used to start Genshin Impact and \
        3DMigoto together with this program when you launch it."
    Pop $0

    ${NSD_CreateCheckBox} 10 47u 80% 20 "Start Genshin Impact and GIMI on program startup"
    Pop $startGameAndGimiCheck
    ${NSD_OnClick} $startGameAndGimiCheck onStartGameAndGIMIChange
    ${NSD_SetState} $startGameAndGimiCheck $startGameAndGimiCheckStatus

    ${NSD_CreateText} 0 75u 75% 12u "$gameDir"
    Pop $gameDirectoryText
    ${NSD_OnChange} $gameDirectoryText onGameDirectoryTextChange

    ${NSD_CreateBrowseButton} 80% 75u 20% 14u "Browse"
    Pop $gameBrowseButton
    ${NSD_OnClick} $gameBrowseButton onGameBrowseButtonClick

    ; Run checks
    Call onGameDirectoryTextChange
    Call onStartGameAndGIMIChange

    nsDialogs::Show
FunctionEnd

Function onGameBrowseButtonClick
    nsDialogs::SelectFileDialog open "$gameDir" ".exe files|*.exe"
    Pop $0

    ${If} $0 != error
    ${AndIf} $0 != ""
        StrCpy $gameDir $0
        ${NSD_SetText} $gameDirectoryText $gameDir
    ${EndIf}
FunctionEnd


Function onGameDirectoryTextChange
    ${NSD_GetText} $gameDirectoryText $gameDir

    ${If} ${FileExists} "$gameDir"
        !insertmacro checkFileName $gameDir "$(gameExecutable)"
    ${Else}
        EnableWindow $parentHwnd 0
    ${EndIf}
FunctionEnd


Function onStartGameAndGIMIChange
    ${NSD_GetState} $startGameAndGimiCheck $startGameAndGimiCheckStatus

    ${If} $startGameAndGimiCheckStatus == 1
        EnableWindow $gameDirectoryText 1
        EnableWindow $gameBrowseButton 1

        ${NSD_GetText} $gameDirectoryText $gameDir

        ${If} ${FileExists} "$gameDir"
            !insertmacro checkFileName $gameDir "$(gameExecutable)"
        ${Else}
            EnableWindow $parentHwnd 0
        ${EndIf}
    ${Else}
        EnableWindow $gameDirectoryText 0
        EnableWindow $gameBrowseButton 0
        EnableWindow $parentHwnd 1
    ${EndIf}
FunctionEnd
