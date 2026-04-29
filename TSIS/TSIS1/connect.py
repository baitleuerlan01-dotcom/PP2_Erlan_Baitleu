import psycopg2
from config import load_config

def connect(config):
    """Создаёт и возвращает новое подключение к БД"""
    try:
        conn = psycopg2.connect(**config)
        print("Connected to PostgreSQL server.")
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"[ERROR] Не удалось подключиться к базе: {error}")
        return None

if __name__ == "__main__":
    config = load_config()
    conn = connect(config)
    if conn:
        conn.close()