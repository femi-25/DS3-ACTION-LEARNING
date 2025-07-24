import psycopg2
import bcrypt
from psycopg2.extras import RealDictCursor

DB_NAME = "mvp_app"
DB_USER = "postgres"
DB_PASS = "Sql.123"
DB_HOST = "localhost"
DB_PORT = "5432"

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_user(user_data):
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT id FROM users WHERE username = %s", (user_data.username,))
    if cur.fetchone():
        cur.close()
        raise Exception("Username already exists")

    cur.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
    if cur.fetchone():
        cur.close()
        raise Exception("Email already exists")

    hashed_pw = hash_password(user_data.password)

    cur.execute("""
        INSERT INTO users (username, email, full_name, hashed_password, role, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id, username, email, full_name, role, created_at
    """, (user_data.username, user_data.email, user_data.full_name, hashed_pw, "user"))

    user = cur.fetchone()
    conn.commit()
    cur.close()
    return user

def get_user_by_username(username: str):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user
