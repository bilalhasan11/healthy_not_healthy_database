import psycopg2
from psycopg2 import pool
from datetime import datetime

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "Namal12345",
    "host": "database-1.cp44esw4ubtb.eu-north-1.rds.amazonaws.com",
    "port": "5432"
}

db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)

def init_db():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email TEXT UNIQUE, password TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS predictions (id SERIAL PRIMARY KEY, user_id INT, timestamp TEXT, audio_name TEXT, result TEXT, audio BYTEA)")
            conn.commit()
    finally:
        db_pool.putconn(conn)

def register_user(email, password):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
            conn.commit()
        return "Signup successful"
    finally:
        db_pool.putconn(conn)

def authenticate_user(email, password):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT id FROM users WHERE email = %s AND password = %s", (username, password))
            user = c.fetchone()
            return {"user_id": user[0]} if user else {"error": "Invalid credentials"}
    finally:
        db_pool.putconn(conn)

def save_prediction(user_id, audio_name, result, audio_data):
    """Saves the prediction along with user_id and audio file"""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                "INSERT INTO predictions (user_id, timestamp, audio_name, result, audio) VALUES (%s, %s, %s, %s, %s)",
                (user_id, timestamp, audio_name, result, psycopg2.Binary(audio_data))
            )
            conn.commit()
    finally:
        db_pool.putconn(conn)

def get_history(user_id):
    """Retrieves the prediction history for a given user"""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT timestamp, audio_name, result FROM predictions WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
            history = [{"timestamp": row[0], "audio_name": row[1], "result": row[2]} for row in c.fetchall()]
        return history
    finally:
        db_pool.putconn(conn)
def get_user_profile(user_id):
    """Fetches user profile details."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT email, fullname, country, city, gender, phone_number FROM users WHERE id = %s", (user_id,))
            user = c.fetchone()
            if user:
                return {
                    "email": user[0],
                    "fullname": user[1],
                    "country": user[2],
                    "city": user[3],
                    "gender": user[4],
                    "phone_number": user[5]
                }
            return {"error": "User not found"}
    finally:
        db_pool.putconn(conn)

def update_user_profile(user_id, fullname, country, city, gender, phone_number):
    """Updates user profile details except username."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("""
                UPDATE users 
                SET fullname = %s, country = %s, city = %s, gender = %s, phone_number = %s 
                WHERE id = %s
            """, (fullname, country, city, gender, phone_number, user_id))
            conn.commit()
        return {"message": "Profile updated successfully"}
    finally:
        db_pool.putconn(conn)
