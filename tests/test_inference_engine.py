import json
import math
from inference_engine import AirExpertEngine, Fact
from unittest.mock import mock_open, patch

MOCK_RULES = {
    "umbrales_OMS": {
        "PM2_5_24h": 15, "PM10_24h": 45, "NO2_24h": 25,
        "O3_8h": 100, "SO2_24h": 40, "CO_24h": 4000
    },
    "recomendaciones": {
        "Buena": ["Actividades sin restricciones."],
        "Moderada": ["Limitar exposición prolongada."],
        "Riesgo moderado": ["Evitar ejercicio intenso."],
        "Riesgo alto": ["Permanecer en interiores."]
    }
}

def test_aqi_buena():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_RULES))):
        eng = AirExpertEngine()
        res = eng.evaluate(Fact(PM2_5_24h=8))
        assert res.label == "Buena"
        assert res.color == "green"
        assert res.aqi_value is not None and res.aqi_value <= 50
        assert res.recommendations

def test_aqi_moderada_y_alerta_umbral():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_RULES))):
        eng = AirExpertEngine()
        res = eng.evaluate(Fact(PM2_5_24h=20, NO2_24h=30))
        assert res.label == "Moderada"
        assert any("NO2_24h supera el umbral OMS" in a for a in res.alerts)

def test_aqi_riesgo_moderado_y_alto():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_RULES))):
        eng = AirExpertEngine()
        res1 = eng.evaluate(Fact(PM2_5_24h=40))
        res2 = eng.evaluate(Fact(PM2_5_24h=80))
        assert res1.label == "Riesgo moderado"
        assert res2.label == "Riesgo alto"