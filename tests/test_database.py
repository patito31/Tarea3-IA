from datetime import datetime
from pathlib import Path
import importlib

def test_save_and_fetch_roundtrip(tmp_path):
    import database as db
    importlib.reload(db)                 # recargar limpio
    db._DB_PATH = tmp_path / "test.db"   # usar BD temporal

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

