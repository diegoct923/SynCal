from flask import request, jsonify,session
from google.oauth2 import id_token
from google.auth.transport import requests
from shared.storage.database import connect_db
from shared.storage.sesiones import obtener_telefono_por_state

import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def google_callback():
    data      = request.get_json()
    token     = data.get("token")
    state     = data.get("state")

    # Obtener tel desde el state
    tel = obtener_telefono_por_state(state)
    if not tel:
        return jsonify({"success": False, "error": "Sesión inválida"}), 403

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID, clock_skew_in_seconds=10)
        email    = idinfo["email"]
        google_id = idinfo["sub"]

        conn = connect_db()
        try:
            with conn.cursor() as cur:
                # Obtener datos actuales del usuario
                cur.execute(
                    "SELECT email, google_id, username FROM squema1.usuario WHERE tel = %s",
                    (tel,)
                )
                row = cur.fetchone()
                email_guardado, google_id_guardado, username = row #type: ignore

                # Si ya tiene email/google_id, verificar que coincidan
                if email_guardado and email_guardado != email:
                    return jsonify({"success": False, "error": "Cuenta de Google no coincide"}), 403
                if google_id_guardado and google_id_guardado != google_id:
                    return jsonify({"success": False, "error": "Cuenta de Google no coincide"}), 403

                # Asociar email y google_id si es la primera vez
                if not email_guardado:
                    cur.execute(
                        """
                        UPDATE squema1.usuario
                        SET email = %s, google_id = %s
                        WHERE tel = %s
                        """,
                        (email, google_id, tel)
                    )
                    conn.commit()

            # Crear sesión Flask
            session["telefono"]  = tel
            session["logged_in"] = True

        finally:
            conn.close()

        return jsonify({
            "success": True,
            "needs_username": username is None  # si no tiene username → ir a registro
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"success": False}), 401