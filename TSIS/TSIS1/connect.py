# connect.py
# Database connection helper

import psycopg2
import psycopg2.extras
from config import DB_CONFIG


def get_connection():
    """Return a new psycopg2 connection using settings from config.py."""
    return psycopg2.connect(**DB_CONFIG)


def get_cursor(conn):
    """Return a DictCursor so rows are accessible by column name."""
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def init_db():
    """
    Run schema.sql and procedures.sql to create / update the database.
    Call this once when setting up the project.
    """
    import os
    base = os.path.dirname(os.path.abspath(__file__))

    with get_connection() as conn:
        with conn.cursor() as cur:
            for filename in ("schema.sql", "procedures.sql"):
                path = os.path.join(base, filename)
                with open(path, "r", encoding="utf-8") as f:
                    sql = f.read()
                cur.execute(sql)
        conn.commit()
    print("Database initialised successfully.")


if __name__ == "__main__":
    init_db()