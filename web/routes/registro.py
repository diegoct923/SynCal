from flask import request, render_template, redirect, session
from shared.storage.database import connect_db
from shared.config.config import BASE_URL
import re

def registro():
    state = request.args.get("state", "")

    # Verificar que tenga sesión activa
    if not session.get("logged_in"):
        return redirect(f"{BASE_URL}/login?state={state}")

    if request.method == "GET":
        return render_template("registro.html", state=state, error=None)

    # POST — guardar username
    username = request.form.get("username", "").strip().lower()

    # Validaciones
    if not username:
        return render_template("registro.html", state=state, error="El username no puede estar vacío.")

    if len(username) < 3 or len(username) > 30:
        return render_template("registro.html", state=state, error="El username debe tener entre 3 y 30 caracteres.")

    if not re.match(r'^[a-z0-9._]+$', username):
        return render_template("registro.html", state=state, error="Solo se permiten letras, números, puntos y guiones bajos.")

    tel = session.get("telefono")

    conn = connect_db()
    try:
        with conn.cursor() as cur:
            # Verificar que el username no esté tomado
            cur.execute(
                "SELECT id FROM squema1.usuario WHERE username = %s",
                (username,)
            )
            if cur.fetchone():
                return render_template("registro.html", state=state, error="Ese username ya está en uso.")

            cur.execute(
                "UPDATE squema1.usuario SET username = %s WHERE tel = %s",
                (username, tel)
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    return redirect(f"{BASE_URL}/calendar?state={state}")
