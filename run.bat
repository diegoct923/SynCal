@echo off

cd /d %~dp0

echo Activando entorno...
call venv\Scripts\activate

echo Levantando servidor Flask...
start cmd /k python main.py

timeout /t 3

echo Levantando ngrok...
start cmd /k ngrok.exe http 5000

echo Configurando webhook automaticamente...
python -m scripts.auto_config

echo ===================================
echo Sistema iniciado
echo Revisar ventanas abiertas
pause