import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple
from datetime import datetime

_DB_PATH = Path("data/air_data.db")


@contextmanager
def _conn():
    """Context manager that ensures the database directory exists,
    enables foreign keys and yields a sqlite3.Connection.
    """
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    # Ensure foreign key constraints are enforced
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_db() -> None:
    """Create the normalized schema: medidas, condiciones, contexto."""
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS medidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pm2_5 REAL,
            pm10 REAL,
            no2 REAL,
            co REAL,
            o3 REAL,
            so2 REAL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS condiciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperatura REAL,
            humedad REAL,
            v_viento REAL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS contexto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zona TEXT,
            hora DATETIME,
            evento_biomasa INTEGER NOT NULL DEFAULT 0,
            quality_level TEXT,
            medida_id INTEGER,
            condicion_id INTEGER,
            FOREIGN KEY (medida_id) REFERENCES medidas(id) ON DELETE CASCADE,
            FOREIGN KEY (condicion_id) REFERENCES condiciones(id) ON DELETE CASCADE
        )
        """)


def save_measurement(data: Dict[str, Any]) -> int:
    """Insert a row into `medidas`.

    Expects keys: pm2_5, pm10, no2, co, o3, so2
    Returns the inserted row id.
    """
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            """
            INSERT INTO medidas (pm2_5, pm10, no2, co, o3, so2)
            VALUES (:pm2_5, :pm10, :no2, :co, :o3, :so2)
            """,
            data,
        )
        return cur.lastrowid


def save_condition(data: Dict[str, Any]) -> int:
    """Insert a row into `condiciones`.

    Expects keys: temperatura, humedad, v_viento
    Returns the inserted row id.
    """
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            """
            INSERT INTO condiciones (temperatura, humedad, v_viento)
            VALUES (:temperatura, :humedad, :v_viento)
            """,
            data,
        )
        return cur.lastrowid


def save_context(data: Dict[str, Any]) -> int:
    """Insert a row into `contexto` linking medidas and condiciones if provided.

    Expects keys: zona, hora, evento_biomasa, quality_level, medida_id, condicion_id
    Returns the inserted row id.
    """
    with _conn() as c:
        cur = c.cursor()
        cur.execute(
            """
            INSERT INTO contexto (zona, hora, evento_biomasa, quality_level, medida_id, condicion_id)
            VALUES (:zona, :hora, :evento_biomasa, :quality_level, :medida_id, :condicion_id)
            """,
            data,
        )
        return cur.lastrowid


def save_full_record(
    measurement: Dict[str, Any],
    condition: Dict[str, Any],
    context_extra: Dict[str, Any] = None,
) -> Tuple[int, int, int]:
    """Atomically save measurement, condition and context linking records.

    - measurement: dict with keys pm2_5, pm10, no2, co, o3, so2
    - condition: dict with keys temperatura, humedad, v_viento
    - context_extra: optional dict with keys zona, hora, evento_biomasa, quality_level

    Returns a tuple (medida_id, condicion_id, contexto_id).
    """
    context_extra = context_extra or {}

    if not context_extra.get('hora'):
        context_extra['hora'] = datetime.now().isoformat(timespec='seconds')

    with _conn() as c:
        cur = c.cursor()

        cur.execute(
            """
            INSERT INTO medidas (pm2_5, pm10, no2, co, o3, so2)
            VALUES (:pm2_5, :pm10, :no2, :co, :o3, :so2)
            """,
            measurement,
        )
        medida_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO condiciones (temperatura, humedad, v_viento)
            VALUES (:temperatura, :humedad, :v_viento)
            """,
            condition,
        )
        condicion_id = cur.lastrowid

        ctx = {
            'zona': context_extra.get('zona'),
            'hora': context_extra.get('hora'),
            'evento_biomasa': context_extra.get('evento_biomasa', 0),
            'quality_level': context_extra.get('quality_level'),
            'medida_id': medida_id,
            'condicion_id': condicion_id,
        }

        cur.execute(
            """
            INSERT INTO contexto (zona, hora, evento_biomasa, quality_level, medida_id, condicion_id)
            VALUES (:zona, :hora, :evento_biomasa, :quality_level, :medida_id, :condicion_id)
            """,
            ctx,
        )
        contexto_id = cur.lastrowid

        return medida_id, condicion_id, contexto_id


def fetch_last_measurements(n: int = 20) -> Iterable[Tuple]:
    with _conn() as c:
        return c.execute(
            """
            SELECT id, timestamp, pm2_5, pm10, no2, co, o3, so2
            FROM medidas ORDER BY id DESC LIMIT ?
            """,
            (n,),
        ).fetchall()


def fetch_recent_context(n: int = 20) -> Iterable[Tuple]:
    with _conn() as c:
        return c.execute(
            """
            SELECT ctx.id, ctx.zona, ctx.hora, ctx.evento_biomasa, ctx.quality_level,
                   m.pm2_5, m.pm10, m.no2, m.co, m.o3, m.so2,
                   cond.temperatura, cond.humedad, cond.v_viento
            FROM contexto ctx
            LEFT JOIN medidas m ON ctx.medida_id = m.id
            LEFT JOIN condiciones cond ON ctx.condicion_id = cond.id
            ORDER BY ctx.id DESC LIMIT ?
            """,
            (n,),
        ).fetchall()
