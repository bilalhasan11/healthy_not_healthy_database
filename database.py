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
            c.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS predictions (id SERIAL PRIMARY KEY, user_id INT, timestamp TEXT, audio_name TEXT, result TEXT, audio BYTEA)")
            conn.commit()
    finally:
        db_pool.putconn(conn)

def register_user(username, password):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
        return "Signup successful"
    finally:
        db_pool.putconn(conn)

def authenticate_user(username, password):
    conn = db_pool.getconn()
    try:
        with conn.cursor() as c:
            c.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
            user = c.fetchone()
            return {"user_id": user[0]} if user else {"error": "Invalid credentials"}
    finally:
        db_pool.putconn(conn)
