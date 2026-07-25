@echo off
chcp 65001 >nul
cls

echo ╔═══════════════════════════════════════════════════════════╗
echo ║     INSTALLATION DES DÉPENDANCES - ReventePro V4          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERREUR : Python n'est pas installé ou non dans le PATH
    echo.
    echo Téléchargez Python 3.9+ depuis : https://www.python.org/downloads/
    echo ⚠️  Lors de l'installation, cochez "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python trouvé
python --version
echo.
echo ⏳ Installation des dépendances en cours...
echo.

REM Installer les dépendances
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERREUR : L'installation a échoué
    echo Vérifiez votre connexion Internet
    pause
    exit /b 1
)

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  ✅ INSTALLATION RÉUSSIE !                                ║
echo ║  Vous pouvez maintenant lancer ReventePro V4              ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
pause
