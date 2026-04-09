from flask import request
import os
import requests
from dotenv import load_dotenv
from app.storage.auth_store import get_phone_from_state, delete_state
from app.storage.user_store import update_user_token, update_user_database
from app.integrations.notion_client_integration import setup_user_database
from config.config import BASE_URL


load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def callback():
    code = request.args.get("code")
    state = request.args.get("state")

    phone = get_phone_from_state(state)

    if not phone:
        return " State inválido"

    #  pedir token a Notion
    response = requests.post(
        "https://api.notion.com/v1/oauth/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        json={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"{BASE_URL}/callback"
        }
    )

    data = response.json()
    token = data.get("access_token")

    if not token:
        print("Error Notion:", data)
        return " Error obteniendo token"

    #  NUEVO → setup automático
    try:
        db_id = setup_user_database(token)
    except Exception as e:
        print(" ERROR SETUP DB:", e)
        return " Error configurando Notion"

    if not db_id:
        return (
            " No se pudo configurar Notion.\n"
            "Asegurate de tener al menos una página disponible."
        )

    #  guardar datos
    update_user_token(phone, token)
    update_user_database(phone, db_id)

    delete_state(state)

    print(f" Usuario {phone} conectado con DB {db_id}")

    return " Notion conectado y listo. Volvé a WhatsApp"