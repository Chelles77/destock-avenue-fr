@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Détecter le chemin du script (fonctionne sur clé USB ou disque dur)
cd /d "%~dp0"

REM Vérifier si on est dans le bon dossier
if not exist "app" (
    echo ❌ Erreur : Dossier 'app' introuvable !
    echo Assurez-vous de lancer ce script depuis le dossier ReventePro_V4
    pause
    exit /b 1
)

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erreur : Python n'est pas installé ou non dans le PATH
    echo Veuillez installer Python 3.9+ depuis https://www.python.org/downloads/
    echo N'oubliez pas de cocher "Add Python to PATH"
    pause
    exit /b 1
)

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║         ReventePro V4 - Destock Avenue FR                ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo ✅ Lancement en cours...
echo 📱 L'app s'ouvrira à : http://127.0.0.1:5000
echo ⏸️  Pour arrêter : Fermer cette fenêtre ou Ctrl+C
echo.
timeout /t 2

REM Lancer l'application
python -m flask run --host=127.0.0.1 --port=5000

pause
