from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from database import init_db
from inference_engine import analyze
import sqlite3

app = Flask(__name__)
DB_NAME = 'air_data.db'

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    result_level = None
    nivel_cont = None
    nivel_meteo = None
    nivel_ctx = None

    if request.method == 'POST':
        try:
            pm2_5 = float(request.form.get('pm2_5'))
            pm10 = float(request.form.get('pm10'))
            no2 = float(request.form.get('no2'))
            co = float(request.form.get('co'))
            o3 = float(request.form.get('o3'))
            so2 = float(request.form.get('so2'))
            temperatura = float(request.form.get('temperatura'))
            humedad = float(request.form.get('humedad'))
            v_viento = float(request.form.get('v_viento'))
            evento_biomasa = int(request.form.get('evento_biomasa', 0))

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medidas (pm2_5, pm10, no2, co, o3, so2)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pm2_5, pm10, no2, co, o3, so2))
            medida_id = cursor.lastrowid
            conn.commit()
            conn.close()

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO condiciones (temperatura, humedad, v_viento)
                VALUES (?, ?, ?)
            """, (temperatura, humedad, v_viento))
            condicion_id = cursor.lastrowid
            conn.commit()
            conn.close()

            result_level, nivel_cont, nivel_meteo, nivel_ctx = analyze(
                pm2_5, pm10, no2, co, o3, so2, temperatura, humedad, v_viento, evento_biomasa
            )

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contexto (hora, evento_biomasa, quality_level, medida_id, condicion_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                evento_biomasa,
                result_level,
                medida_id,
                condicion_id
            ))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))

        except ValueError:
            pass

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    measurements = cursor.execute(
        """
        SELECT 
            medidas.timestamp,
            medidas.pm2_5,
            medidas.pm10,
            medidas.no2,
            medidas.co,
            medidas.o3,
            medidas.so2,
            contexto.quality_level
        FROM medidas
        JOIN contexto ON contexto.medida_id = medidas.id
        ORDER BY medidas.id DESC
        LIMIT 10
        """
    ).fetchall()
    conn.close()

    return render_template(
        'index.html',
        measurements=measurements,
        result_level=result_level,
        nivel_cont=nivel_cont,
        nivel_meteo=nivel_meteo,
        nivel_ctx=nivel_ctx
    )

if __name__ == '__main__':
    app.run(debug=True)
