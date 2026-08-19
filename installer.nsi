; Script de Instalador NSIS para Sistema Financeiro
; Requer NSIS (https://nsis.sourceforge.io/)

!define APPNAME "Sistema Financeiro - Loja Jerônimo Rosado 1994"
!define COMPANYNAME "Loja Jerônimo Rosado 1994"
!define DESCRIPTION "Sistema de Gestão Financeira Maçônica"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/seu-repositorio" 
!define UPDATEURL "https://github.com/seu-repositorio"
!define ABOUTURL "https://github.com/seu-repositorio"
!define INSTALLSIZE 50000

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\${APPNAME}"

Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

Section "install"
    SectionIn RO
    
    ; Instalar arquivos
    SetOutPath $INSTDIR
    File "dist\SistemaFinanceiro.exe"
    File "logo.png"
    
    ; Criar atalho na área de trabalho
    CreateShortCut "$DESKTOP\Sistema Financeiro.lnk" "$INSTDIR\SistemaFinanceiro.exe" "" "$INSTDIR\logo.png" 0
    
    ; Criar atalho no Menu Iniciar
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Sistema Financeiro.lnk" "$INSTDIR\SistemaFinanceiro.exe" "" "$INSTDIR\logo.png" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
    
    ; Criar desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Adicionar ao registro para desinstalação
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$INSTDIR\uninstall.exe /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionBuild" ${VERSIONBUILD}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
SectionEnd

Section "uninstall"
    ; Remover atalhos
    Delete "$DESKTOP\Sistema Financeiro.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Sistema Financeiro.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    ; Remover arquivos
    Delete $INSTDIR\SistemaFinanceiro.exe
    Delete $INSTDIR\logo.png
    Delete $INSTDIR\uninstall.exe
    Delete $INSTDIR\financas_loja.db
    
    ; Remover diretório se vazio
    RMDir $INSTDIR
    
    ; Remover do registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
