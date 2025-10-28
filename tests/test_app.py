import types
import importlib
from inference_engine import InferenceResult

def test_index_get(monkeypatch):
    # Importar el módulo web
    import app as web
    dummy_rows = [
        (1, "Centro", None, 0, "Buena", 10.0, 20.0, 5.0, 0.5, 30.0, 5.0, 22.0, 40.0, None)
    ]
    monkeypatch.setattr(web, "fetch_recent_context", lambda n=10: dummy_rows)

    client = web.app.test_client()
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Historial de Inferencias" in html
    assert "Centro" in html

def test_index_post_evaluates_and_saves(monkeypatch):
    import app as web

    def fake_eval(_fact):
        return InferenceResult(
            label="Moderada", color="yellow", explanation="ok",
            recommendations=["r1"], alerts=[], aqi_value=80
        )
    monkeypatch.setattr(web.engine, "evaluate", fake_eval)

    called = {"save": False, "csv": False}
    def fake_save_full_record(m, c, x):
        called["save"] = True
        return (1, 1, 1)
    def fake_append_to_csv(m, c, x, label):
        called["csv"] = True

    monkeypatch.setattr(web, "save_full_record", fake_save_full_record)
    monkeypatch.setattr(web, "append_to_csv", fake_append_to_csv)
    monkeypatch.setattr(web, "fetch_recent_context", lambda n=10: [])

    client = web.app.test_client()
    res = client.post(
        "/",
        data={
            "zona": "Norte", "evento_biomasa": "0",
            "pm25": "22", "pm10": "22", "no2": "22", "o3": "22",
            "so2": "22", "co": "22", "temp": "22", "rh": "22",
        },
        follow_redirects=False,
    )
    assert res.status_code in (302, 303)
    assert called["save"] and called["csv"]