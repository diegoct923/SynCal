#!/bin/bash

echo "Activando entorno..."
source venv/bin/activate

echo "Levantando servidor Flask..."
kitty bash -c "python app.py; exec bash" &

sleep 3

echo "Levantando ngrok..."
kitty bash -c "ngrok http 5000; exec bash" &

echo "Configurando webhook automaticamente..."
python auto_config.py

echo "==================================="
echo "Sistema iniciado"
echo "Revisar ventanas abiertas"
read -p "Presiona Enter para continuar..."
