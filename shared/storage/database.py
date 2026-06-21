import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRESDB_NAME = os.getenv("POSTGRESDB_NAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
OPTIONS = os.getenv("OPTIONS")



def connect_db(): 
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRESDB_NAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT,
        options=OPTIONS
    )
    return conn
