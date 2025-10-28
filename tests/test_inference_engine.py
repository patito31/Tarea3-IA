import math
from inference_engine import AirExpertEngine, Fact

def test_aqi_buena():
    eng = AirExpertEngine()
    res = eng.evaluate(Fact(PM2_5_24h=8))
    assert res.label == "Buena"
    assert res.color == "green"
    assert res.aqi_value is not None and res.aqi_value <= 50
    assert res.recommendations  # hay recomendaciones para el nivel

def test_aqi_moderada_y_alerta_umbral():
    eng = AirExpertEngine()
    # NO2_24h > 25 (umbral en data/air_rules.json) debe generar alerta
    res = eng.evaluate(Fact(PM2_5_24h=20, NO2_24h=30))
    assert res.label == "Moderada"
    assert any("NO2_24h supera el umbral OMS" in a for a in res.alerts)

def test_aqi_riesgo_moderado_y_alto():
    eng = AirExpertEngine()
    res1 = eng.evaluate(Fact(PM2_5_24h=40))
    res2 = eng.evaluate(Fact(PM2_5_24h=80))
    assert res1.label == "Riesgo moderado"
    assert res2.label == "Riesgo alto"