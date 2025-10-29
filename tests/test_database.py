from datetime import datetime
from pathlib import Path
import importlib
from unittest.mock import MagicMock, patch

def test_save_and_fetch_roundtrip(tmp_path):
    import database as db
    importlib.reload(db)                
    db._DB_PATH = tmp_path / "test.db"   

    db.init_db()

    medida = {"pm2_5": 12.3, "pm10": 30, "no2": 10, "co": 0.5, "o3": 20, "so2": 5}
    condicion = {"temperatura": 22, "humedad": 45, "v_viento": None}
    ctx_extra = {"zona": "Centro", "hora": None, "evento_biomasa": 0, "quality_level": "Buena"}

    m_id, c_id, ctx_id = db.save_full_record(medida, condicion, ctx_extra)
    assert m_id > 0 and c_id > 0 and ctx_id > 0

    rows = db.fetch_recent_context(1)
    assert len(rows) == 1
    r = rows[0]
    assert r[1] == "Centro"
    assert r[4] == "Buena"
    assert r[5] == 12.3
    assert r[12] == 45

def test_save_full_record_calls_correct_sql():
    import database as db
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 42
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = lambda self: mock_conn
    mock_conn.__exit__ = lambda *args: None

    with patch("database._conn", return_value=mock_conn):
        medida = {"pm2_5": 12.3, "pm10": 30, "no2": 10, "co": 0.5, "o3": 20, "so2": 5}
        condicion = {"temperatura": 22, "humedad": 45, "v_viento": None}
        ctx_extra = {"zona": "Centro", "hora": None, "evento_biomasa": 0, "quality_level": "Buena"}

        m_id, c_id, ctx_id = db.save_full_record(medida, condicion, ctx_extra)

        assert mock_cursor.execute.call_count == 3
        assert m_id == 42
        assert c_id == 42
        assert ctx_id == 42
def test_fetch_recent_context_returns_rows():
    import database as db
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, "Centro", None, 0, "Buena", 12.3, 30, 10, 0.5, 20, 5, 22, 45, None)
    ]
    mock_conn.execute.return_value = mock_cursor
    mock_conn.__enter__ = lambda self: mock_conn
    mock_conn.__exit__ = lambda *args: None

    with patch("database._conn", return_value=mock_conn):
        rows = db.fetch_recent_context(1)
        assert len(rows) == 1
        assert rows[0][1] == "Centro" 
        assert rows[0][4] == "Buena"   

