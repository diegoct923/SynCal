from flask import request, jsonify,session
from google.oauth2 import id_token
from google.auth.transport import requests
from app.storage.database import connect_db

import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def google_callback():

    # JSON enviado desde frontend
    data = request.get_json()

    # token JWT de Google
    token = data.get("token")

    # teléfono del usuario WhatsApp
    telefono = data.get("telefono")

    try:

        # validar token con Google
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # datos reales devueltos por Google
        email = idinfo["email"]
        name = idinfo.get("name")

        print("EMAIL:", email)
        print("NAME:", name)
        print("TELEFONO:", telefono)

        # conectar PostgreSQL
        conn = connect_db()

        try:

            with conn.cursor() as cur:

                # vincular email Google con teléfono WhatsApp
                cur.execute("""
                    UPDATE usuario
                    SET email = %s
                    WHERE tel = %s
                """, (email, telefono))

                conn.commit()

                print("Email vinculado correctamente")

                # crear sesión Flask
            session["telefono"] = telefono
            session["logged_in"] = True

        finally:

            conn.close()

        return jsonify({
            "success": True
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "success": False
        }), 401
    



