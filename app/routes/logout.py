from flask import session, redirect, request
from config.config import BASE_URL



def logout():
    
    state = request.args.get("state", "")
    session.clear()
    return redirect(f"{BASE_URL}/login?state={state}")