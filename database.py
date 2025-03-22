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
            c.execute("CREATE TABLE IF NOT EXISTS users (user_id SERIAL PRIMARY KEY, email TEXT UNIQUE, password TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS predictions (pred_id SERIAL PRIMARY KEY, user_id INT, timestamp TEXT, audio_name TEXT, result TEXT, audio BYTEA)")
            c.execute("CREATE TABLE IF NOT EXISTS farm (farm_id SERIAL PRIMARY KEY, user_id INT UNIQUE, fullname TEXT, country TEXT, city TEXT, zip TEXT, hives INT DEFAULT 0)")
            conn.commit()
    finally:
        db_pool.putconn(conn)

def register_user(fullname, email, password):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)", (fullname, email, password))
            conn.commit()
        return "Signup successful"
    finally:
        db_pool.putconn(conn)

def authenticate_user(email, password):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT user_id FROM users WHERE email = %s AND password = %s", (email, password))
            user = c.fetchone()
            return {"user_id": user[0]} if user else {"error": "Invalid credentials"}
    finally:
        db_pool.putconn(conn)

import psycopg2
from datetime import datetime
from db_config import db_pool  # Ensure you have a database connection pool set up

def save_prediction(user_id, audio_name, result, file_id):
    """Saves the prediction data (excluding the actual audio) in the database."""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                "INSERT INTO predictions (user_id, timestamp, audio_name, result, file_id) VALUES (%s, %s, %s, %s, %s)",
                (user_id, timestamp, audio_name, result, file_id)
            )
            conn.commit()
    finally:
        db_pool.putconn(conn)


def get_history(user_id):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT timestamp, audio_name, result FROM predictions WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
            return [{"timestamp": row[0], "audio_name": row[1], "result": row[2]} for row in c.fetchall()]
    finally:
        db_pool.putconn(conn)

def get_user_profile(user_id):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT email, fullname, country, city, gender, phone_number FROM users WHERE user_id = %s", (user_id,))
            user = c.fetchone()
            return {
                "email": user[0], "fullname": user[1], "country": user[2], 
                "city": user[3], "gender": user[4], "phone_number": user[5]
            } if user else {"error": "User not found"}
    finally:
        db_pool.putconn(conn)

def update_user_profile(user_id, fullname, country, city, gender, phone_number):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("""
                UPDATE users 
                SET fullname = %s, country = %s, city = %s, gender = %s, phone_number = %s 
                WHERE user_id = %s
            """, (fullname, country, city, gender, phone_number, user_id))
            conn.commit()
        return {"message": "Profile updated successfully"}
    finally:
        db_pool.putconn(conn)

def get_farm_details_from_db(user_id):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            # Updated query to include farm_id
            c.execute("SELECT farm_id, fullname, country, city, zip, hives FROM farm WHERE user_id = %s", (user_id,))
            farm = c.fetchone()
            # Include farm_id in the returned JSON
            return {
                "farm_id": farm[0],    # Added farm_id
                "fullname": farm[1],   # Shifted indices due to farm_id being first
                "country": farm[2],
                "city": farm[3],
                "zip": farm[4],
                "hives": farm[5]
            } if farm else None
    finally:
        db_pool.putconn(conn)

def update_farm_details_in_db(user_id, fullname, country, city, zip_code):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT farm_id FROM farm WHERE user_id = %s", (user_id,))
            existing_farm = c.fetchone()

            if existing_farm:
                c.execute("""
                    UPDATE farm 
                    SET fullname = %s, country = %s, city = %s, zip = %s 
                    WHERE user_id = %s
                """, (fullname, country, city, zip_code, user_id))
            else:
                c.execute("""
                    INSERT INTO farm (user_id, fullname, country, city, zip) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, fullname, country, city, zip_code))

            conn.commit()
        return {"message": "Farm details updated successfully"}
    finally:
        db_pool.putconn(conn)
def get_farm_detailss_from_db(user_id):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT farm_id FROM farm WHERE user_id = %s", (user_id,))
            farm = c.fetchone()
            return {"farm_id": farm[0]} if farm else None
    finally:
        db_pool.putconn(conn)

def get_hives_from_db(farm_id):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT hive_id, hive_number FROM Hive WHERE farm_id = %s ORDER BY hive_number", (farm_id,))
            return [{"hive_id": row[0], "hive_number": row[1]} for row in c.fetchall()]
    finally:
        db_pool.putconn(conn)

def get_hive_detail_from_db(hive_id):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute(
                "SELECT hive_number, bee_type, number_of_frames, creation_date, health_status, notes FROM Hive WHERE hive_id = %s",
                (hive_id,)
            )
            row = c.fetchone()  # Use fetchone() for a single row
            if row:
                return {
                    "hive_number": row[0],
                    "bee_type": row[1],
                    "number_of_frames": row[2],
                    "creation_date": row[3],
                    "health_status": row[4],
                    "notes": row[5]
                }
            return {"error": "Hive not found"}  # Return error if no hive exists
    finally:
        db_pool.putconn(conn)
