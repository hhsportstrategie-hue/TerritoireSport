@echo off
title TerritoireSport Dashboard
cd /d %~dp0

echo ============================================================
echo   TerritoireSport — Dashboard local
echo ============================================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou pas dans le PATH.
    echo Télécharge-le sur https://python.org/downloads
    echo Coche "Add Python to PATH" pendant l'installation.
    pause
    exit /b 1
)

REM Installer les dépendances si nécessaire
echo [1/3] Vérification des dépendances...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installation de fastapi et uvicorn...
    pip install fastapi uvicorn --quiet
)

REM Lancer le serveur
echo [2/3] Démarrage du serveur...
echo.
echo   → Dashboard disponible sur http://localhost:8765
echo   → Ouvre cette URL dans ton navigateur
echo.
echo [3/3] Appuie sur Ctrl+C dans cette fenêtre pour arrêter.
echo.

REM Ouvrir le navigateur après 2 secondes
start /min cmd /c "timeout /t 2 >nul && start http://localhost:8765"

python dashboard_server.py

pause