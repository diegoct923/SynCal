from flask import request, render_template

import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def login():

    state = request.args.get("state", "")
    print(GOOGLE_CLIENT_ID)
    return render_template(
        "login.html",
        state=state,
        TU_GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID 
    )

