from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
from pathlib import Path

# Ruta base de conocimiento
_RULES_PATH = Path("data/air_rules.json")

@dataclass
class Fact:
    PM2_5_24h: Optional[float] = None
    PM10_24h: Optional[float] = None
    NO2_24h: Optional[float] = None
    O3_8h: Optional[float] = None
    SO2_24h: Optional[float] = None
    CO_24h: Optional[float] = None
    temp: Optional[float] = None
    rh: Optional[float] = None

@dataclass
class InferenceResult:
    label: str
    color: str
    explanation: str
    recommendations: List[str]
    alerts: List[str]
    aqi_value: Optional[int] = None

class AirExpertEngine:
    def __init__(self):
        with open(_RULES_PATH, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

    def _calc_aqi_pm25(self, pm25: float) -> int:
        """Cálculo simplificado de AQI PM2.5 (EPA 2024)"""
        bp = [
            (0, 9, 0, 50),
            (9.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 125.4, 151, 200)
        ]
        for Cl, Ch, Il, Ih in bp:
            if Cl <= pm25 <= Ch:
                return round(((Ih - Il) / (Ch - Cl)) * (pm25 - Cl) + Il)
        return 201  # Si excede máximo, se considera riesgo alto

    def evaluate(self, fact: Fact) -> InferenceResult:
        just = []
        recs = []
        alerts = []
        color = "green"
        label = "Buena"
        aqi_value = None

        # 1️⃣ Calcular AQI PM2.5 si hay dato
        if fact.PM2_5_24h is not None:
            aqi_value = self._calc_aqi_pm25(fact.PM2_5_24h)
            just.append(f"AQI PM2.5 = {aqi_value} basado en concentración de {fact.PM2_5_24h} µg/m³.")

            if aqi_value <= 50:
                label, color = "Buena", "green"
            elif aqi_value <= 100:
                label, color = "Moderada", "yellow"
            elif aqi_value <= 150:
                label, color = "Riesgo moderado", "orange"
            else:
                label, color = "Riesgo alto", "red"

            # Recomendaciones según nivel
            recs.extend(self.rules["recomendaciones"][label])

        # 2️⃣ Revisar gases según umbrales OMS
        for gas, limit in self.rules["umbrales_OMS"].items():
            val = getattr(fact, gas, None)
            if val is not None and val > limit:
                msg = f"{gas} supera el umbral OMS ({val} > {limit})."
                alerts.append(msg)
                just.append(msg)

        # 3️⃣ Contexto ambiental extra
        if fact.temp and fact.temp > 30 and fact.PM2_5_24h and fact.PM2_5_24h > 35:
            alerts.append("Condiciones calurosas con alta concentración de partículas.")
            recs.append("Evite actividades al aire libre prolongadas.")

        explanation = " | ".join(just) if just else "Todos los valores dentro de los rangos recomendados."
        return InferenceResult(
            label=label,
            color=color,
            explanation=explanation,
            recommendations=list(set(recs)),
            alerts=alerts,
            aqi_value=aqi_value
        )
