import psycopg2

try:
    conn = psycopg2.connect(
        dbname="mvp_app",
        user="postgres",
        password="Sql.123",
        host="localhost",
        port="5432"
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
