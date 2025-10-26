DB_NAME = 'air_data.db'

# --- Clasificación de contaminantes ---
def classify_pm25(x):
    return "Buena" if x <= 12 else "Moderada" if x <= 35.4 else "Mala" if x <= 55.4 else "Alerta"

def classify_pm10(x):
    return "Buena" if x <= 54 else "Moderada" if x <= 154 else "Mala" if x <= 254 else "Alerta"

def classify_no2(x):
    return "Buena" if x <= 53 else "Moderada" if x <= 100 else "Mala" if x <= 360 else "Alerta"

def classify_co(x):
    return "Buena" if x <= 4.4 else "Moderada" if x <= 9.4 else "Mala" if x <= 12.4 else "Alerta"

def classify_o3(x):
    return "Buena" if x <= 70 else "Moderada" if x <= 95 else "Mala" if x <= 115 else "Alerta"

def classify_so2(x):
    return "Buena" if x <= 35 else "Moderada" if x <= 75 else "Mala" if x <= 185 else "Alerta"

def overall_level(levels):
    orden = ["Buena", "Moderada", "Mala", "Alerta"]
    return max(levels, key=lambda x: orden.index(x))


# --- Clasificación meteorológica ---
def classify_meteorologia(temp, hr, v_viento):
    puntos = 1  # Normal base

    if v_viento < 2:
        puntos += 1  # baja ventilación → peor
    elif v_viento > 6:
        puntos -= 1  # dispersión → mejor

    if temp > 30:
        puntos += 1  # calor → peor
    elif temp < 10:
        puntos -= 1  # frío → mejor

    if hr > 70:
        puntos -= 1  # humedad alta → mejor
    elif hr < 30:
        puntos += 1  # aire seco → peor

    if puntos < 0:
        puntos = 0
    elif puntos > 3:
        puntos = 3

    return ["Buena", "Moderada", "Mala", "Alerta"][puntos]


# --- Clasificación de contexto ---
def classify_contexto(evento_biomasa):
    return "Mala" if evento_biomasa == 1 else "Buena"


# --- Análisis integral ---
def analyze(pm2_5, pm10, no2, co, o3, so2, temp, hr, v_viento, evento_biomasa):
    niveles_cont = [
        classify_pm25(pm2_5),
        classify_pm10(pm10),
        classify_no2(no2),
        classify_co(co),
        classify_o3(o3),
        classify_so2(so2)
    ]
    nivel_contaminacion = overall_level(niveles_cont)
    nivel_meteo = classify_meteorologia(temp, hr, v_viento)
    nivel_contexto = classify_contexto(evento_biomasa)

    # Convertir niveles a números
    orden = ["Buena", "Moderada", "Mala", "Alerta"]
    puntaje = round(
        (orden.index(nivel_contaminacion) * 0.6 +
         orden.index(nivel_meteo) * 0.3 +
         (1 if nivel_contexto == "Mala" else 0) * 0.1)
    )
    nivel_final = orden[min(puntaje, 3)]

    return nivel_final, nivel_contaminacion, nivel_meteo, nivel_contexto

