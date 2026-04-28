import psycopg2

def connect_db(): 
    
    conn = psycopg2.connect(
        host="186.52.158.13",
        database="syncal",
        user="postgres",
        password="asddsa",  
        port="5432",
        options="-c search_path=squema1"
    )
    
    return conn
#186.50.89.1