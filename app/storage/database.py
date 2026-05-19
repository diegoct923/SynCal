import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

def connect_db(): 
    conn = psycopg2.connect(
        host="wicaldb.duckdns.org",
        database="syncal",
        user="postgres",
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT,
        options="-c search_path=squema1"
    )

    return conn