@echo off
echo ========================================
echo Build do Instalador - Sistema Financeiro
echo ========================================
echo.

echo [1/4] Instalando dependencias...
pip install -r requirements.txt
pip install pyinstaller pywin32
echo.

echo [2/4] Gerando executavel com PyInstaller...
python build_exe.py
echo.

echo [3/4] Verificando se o executavel foi criado...
if exist "dist\SistemaFinanceiro.exe" (
    echo Executavel criado com sucesso!
) else (
    echo ERRO: Executavel nao foi criado. Verifique os erros acima.
    pause
    exit /b 1
)
echo.

echo [4/4] Gerando instalador com NSIS...
echo Certifique-se de que o NSIS esta instalado em: C:\Program Files (x86)\NSIS\makensis.exe
echo.

if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
    echo Instalador gerado com sucesso!
) else if exist "C:\Program Files\NSIS\makensis.exe" (
    "C:\Program Files\NSIS\makensis.exe" installer.nsi
    echo Instalador gerado com sucesso!
) else (
    echo ERRO: NSIS nao encontrado. Por favor, instale o NSIS em: https://nsis.sourceforge.io/
    echo Depois, execute manualmente: makensis.exe installer.nsi
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build concluido com sucesso!
echo O instalador esta na pasta atual.
echo ========================================
pause
