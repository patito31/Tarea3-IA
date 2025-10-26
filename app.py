from flask import Flask, render_template, request, redirect, url_for

# inference / acquisition
from inference_engine import AirExpertEngine, Fact
from acquisition_module import SensorInput, to_fact_dict

# database helpers (normalizado)
from database import (
    init_db,
    save_measurement,
    save_condition,
    save_context,
    save_full_record,
    fetch_recent_context,
)

app = Flask(__name__)


def parse_float(v):
    try:
        return float(v) if v not in ("", None) else None
    except (ValueError, TypeError):
        return None


# Inicializar BDD y motor
engine = AirExpertEngine()
init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        # Construir SensorInput desde distintos posibles nombres de campo
        data = SensorInput(
            PM2_5_24h=(parse_float(request.form.get('pm25'))
                       or parse_float(request.form.get('pm2_5'))
                       or parse_float(request.form.get('pm2_5_24h'))),
            PM10_24h=(parse_float(request.form.get('pm10'))
                      or parse_float(request.form.get('pm_10'))),
            NO2_24h=parse_float(request.form.get('no2')),
            O3_8h=parse_float(request.form.get('o3')),
            SO2_24h=parse_float(request.form.get('so2')),
            CO_24h=parse_float(request.form.get('co')),
            temp=parse_float(request.form.get('temp')),
            rh=parse_float(request.form.get('rh')),
        )

        # Evaluar con motor experto
        fact = Fact(**to_fact_dict(data))
        result = engine.evaluate(fact)

        # Guardar todo en una sola llamada (medida + condición + contexto)
        zona = request.form.get('zona') or None
        evento = request.form.get('evento_biomasa')
        try:
            evento_val = int(evento) if evento not in (None, "") else 0
        except ValueError:
            evento_val = 0

        medida = {
            'pm2_5': data.PM2_5_24h,
            'pm10': data.PM10_24h,
            'no2': data.NO2_24h,
            'co': data.CO_24h,
            'o3': data.O3_8h,
            'so2': data.SO2_24h,
        }
        condicion = {
            'temperatura': data.temp,
            'humedad': data.rh,
            'v_viento': None,
        }
        contexto_extra = {
            'zona': zona,
            'hora': None,
            'evento_biomasa': evento_val,
            'quality_level': result.label,
        }

        save_full_record(medida, condicion, contexto_extra)

        return redirect(url_for('index'))

    # Mostrar historial: contexto reciente (incluye join con medidas/condiciones)
    history = fetch_recent_context(10)
    return render_template('index.html', result=result, history=history)


if __name__ == '__main__':
    app.run(debug=True)