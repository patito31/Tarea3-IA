import csv
from datetime import datetime
from database import save_measurement, save_condition, save_context
from inference_engine import analyze  # motor de inferencia

def acquire_and_save_single_data(csv_path='data/initial_data.csv'):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #contaminantes
            data_m = {
                "pm2_5": float(row.get("pm2_5", 0)),
                "pm10": float(row.get("pm10", 0)),
                "no2": float(row.get("no2", 0)),
                "co": float(row.get("co", 0)),
                "o3": float(row.get("o3", 0)),
                "so2": float(row.get("so2", 0))
            }
            save_measurement(data_m)

            #condiciones meteorológicas
            data_c = {
                "temperatura": float(row.get("temperatura", 0)),
                "humedad": float(row.get("humedad", 0)),
                "v_viento": float(row.get("v_viento", 0))
            }
            save_condition(data_c)

            # Análisis de calidad del aire
            result_level, nivel_cont, nivel_meteo, nivel_ctx = analyze(
                data_m["pm2_5"],
                data_m["pm10"],
                data_m["no2"],
                data_m["co"],
                data_m["o3"],
                data_m["so2"],
                data_c["temperatura"],
                data_c["humedad"],
                data_c["v_viento"],
                int(row.get("evento_biomasa", 0))
            )
            #contexto
            data_x = {
                "hora": datetime.now().isoformat(),
                "evento_biomasa": int(row.get("evento_biomasa", 0)),
                "quality_level": result_level,
                "medida_id": None,
                "condicion_id": None
            }
            save_context(data_x)

            #revisar que guarde el registro en http://127.0.0.1:5000
            print("Datos guardados desde CSV:")
            print("Medidas:", data_m)
            print("Condiciones:", data_c)
            print("Diagnóstico general:", result_level)
            print("Contexto:", data_x)
            break  
