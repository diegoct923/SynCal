from flask import request, render_template

import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def login():

    telefono = request.args.get("telefono", "")
    print(GOOGLE_CLIENT_ID)
    return render_template(
        "login.html",
        telefono=telefono,
        TU_GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID 
    )

