import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",       # Your MySQL server
        user="root",   # MySQL username
        password="27@okay19", # MySQL password
        database="math"  # Your database name
    )
    return conn
