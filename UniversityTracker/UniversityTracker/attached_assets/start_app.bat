@echo off
echo Benvenuto in University Career Manager!
echo.
echo Verifica dell'installazione di Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python non è installato o non è nel PATH.
    echo Per favore installa Python da https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

echo Installazione delle dipendenze necessarie...
pip install PyQt5 matplotlib

echo.
echo Avvio dell'applicazione...
python main.py

pause