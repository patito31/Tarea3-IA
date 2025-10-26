from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SensorInput(BaseModel):
    """Datos provenientes de sensores o formulario (µg/m³, °C, %)"""
    PM2_5_24h: Optional[float] = Field(None, ge=0, description="PM2.5 promedio 24h (µg/m³)")
    PM10_24h: Optional[float] = Field(None, ge=0, description="PM10 promedio 24h (µg/m³)")
    NO2_24h: Optional[float] = Field(None, ge=0, description="Dióxido de nitrógeno (µg/m³)")
    O3_8h: Optional[float] = Field(None, ge=0, description="Ozono troposférico (µg/m³)")
    SO2_24h: Optional[float] = Field(None, ge=0, description="Dióxido de azufre (µg/m³)")
    CO_24h: Optional[float] = Field(None, ge=0, description="Monóxido de carbono (µg/m³)")
    temp: Optional[float] = Field(None, description="Temperatura ambiente (°C)")
    rh: Optional[float] = Field(None, ge=0, le=100, description="Humedad relativa (%)")

def to_fact_dict(inp: "SensorInput") -> Dict[str, Any]:
    """Convierte los datos validados en diccionario limpio"""
    return {
        "PM2_5_24h": inp.PM2_5_24h,
        "PM10_24h": inp.PM10_24h,
        "NO2_24h": inp.NO2_24h,
        "O3_8h": inp.O3_8h,
        "SO2_24h": inp.SO2_24h,
        "CO_24h": inp.CO_24h,
        "temp": inp.temp,
        "rh": inp.rh
    }
