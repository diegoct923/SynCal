import requests

def get_ngrok_url():
    try:
        res = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = res.json()

        for tunnel in data["tunnels"]:
            url = tunnel["public_url"]
            print("Encontrado:", url)

            if url.startswith("https"):
                return url
    except Exception as e:
        print("Error obteniendo ngrok URL:", e)

    return None