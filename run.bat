@echo off

echo Activando entorno...
call venv\Scripts\activate

echo Levantando servidor Flask...
start cmd /k python app.py

timeout /t 3

echo Levantando ngrok...
start cmd /k ngrok http 5000

echo Configurando webhook automaticamente...
python auto_config.py

echo ===================================
echo Sistema iniciado
echo Revisar ventanas abiertas
pause