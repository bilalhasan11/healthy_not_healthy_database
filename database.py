# database.py
import psycopg2
from psycopg2 import pool
from datetime import datetime

# Database configuration (replace with your RDS details)
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "Namal12345",
    "host": "database-1.cp44esw4ubtb.eu-north-1.rds.amazonaws.com",
    "port": "5432"
}

# Connection pool for efficiency
db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)

def init_db():
    """Initialize the PostgreSQL database and create the predictions table."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS predictions 
                         (id SERIAL PRIMARY KEY, 
                          timestamp TEXT, 
                          audio_name TEXT, 
                          result TEXT, 
                          audio BYTEA)''')
            conn.commit()
    finally:
        db_pool.putconn(conn)

def save_prediction(audio_name, result, audio_data):
    """Save a prediction to the database."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("INSERT INTO predictions (timestamp, audio_name, result, audio) VALUES (%s, %s, %s, %s)",
                      (timestamp, audio_name, result, psycopg2.Binary(audio_data)))
            conn.commit()
    finally:
        db_pool.putconn(conn)

def get_history():
    """Fetch all predictions from the database."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT timestamp, audio_name, result FROM predictions ORDER BY timestamp DESC")
            rows = c.fetchall()
            return [{"timestamp": row[0], "audio_name": row[1], "result": row[2]} for row in rows]
    finally:
        db_pool.putconn(conn)
