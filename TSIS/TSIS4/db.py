
import psycopg2
import psycopg2.extras
from config import DB_CONFIG


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def _connect():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Create tables if they don't exist. Returns True on success."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        return False


def get_or_create_player(username: str) -> int | None:
    """Return player id, inserting if necessary."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) "
                    "ON CONFLICT (username) DO NOTHING",
                    (username,)
                )
                cur.execute("SELECT id FROM players WHERE username = %s", (username,))
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        return None



def save_result(username: str, score: int, level_reached: int) -> bool:
    """Save a game session. Returns True on success."""
    try:
        player_id = get_or_create_player(username)
        if player_id is None:
            return False
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (player_id, score, level_reached)
                )
        return True
    except Exception as e:
        print(f"[DB] save_result error: {e}")
        return False


def get_personal_best(username: str) -> int:
    """Return the player's all-time best score (0 if none)."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(MAX(gs.score), 0)
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    WHERE p.username = %s
                    """,
                    (username,)
                )
                row = cur.fetchone()
                return row[0] if row else 0
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0


def get_top10() -> list[dict]:
    """Return the Top-10 all-time scores as list of dicts."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                        p.username,
                        gs.score,
                        gs.level_reached,
                        gs.played_at::date AS played_date
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    ORDER BY gs.score DESC
                    LIMIT 10
                    """
                )
                return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[DB] get_top10 error: {e}")
        return []