import time
from ngrok_utils import get_ngrok_url
from notifier import update_webhook

CONFIG_FILE = "config.py"

print("Esperando ngrok...")

url = None
for _ in range(10):
    url = get_ngrok_url()
    if url:
        break
    time.sleep(2)

if url:
    print("URL encontrada:", url)

    # 🔥 actualizar config.py
    with open(CONFIG_FILE, "w") as f:
        f.write(f'BASE_URL = "{url}"\n')

    update_webhook(url)
else:
    print("No se pudo obtener URL de ngrok")