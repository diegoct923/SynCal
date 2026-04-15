import psycopg2

def connect_db(): 
    
    conn = psycopg2.connect(
        host="localhost",
        database="syncal",
        user="postgres",
        password="asddsa",  
        port="5432",
        options="-c search_path=squema1"
    )
    
    return conn
