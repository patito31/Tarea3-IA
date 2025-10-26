from flask import Flask, render_template, request, redirect, url_for
from database import init_db, sqlite3
from acquisition_module import acquire_and_save_single_data
from inference_engine import analyze_and_update 

app = Flask(__name__)
DB_NAME = 'air_data.db'

# 1. Inicializar la BDD al inicio
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 2. Recepción de datos desde la interfaz (Módulo de Adquisición)
        try:
            pm2_5 = float(request.form.get('pm2_5'))
            pm10 = float(request.form.get('pm10'))
            no2 = float(request.form.get('no2'))
            co = float(request.form.get('co'))
            
            # Guardar la medición inicial en la BDD
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO measurements (pm2_5, pm10, no2, co)
                VALUES (?, ?, ?, ?)
            """, (pm2_5, pm10, no2, co))
            new_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # 3. Analizar los datos y actualizar el resultado (Motor de Inferencia)
            result_level = analyze_and_update(new_id, pm2_5, pm10, no2, co)
            
            return redirect(url_for('index'))

        except ValueError:
            # Manejar error si la entrada no es un número
            pass 

    # 4. Mostrar Resultados (Interfaz)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Obtener las 10 últimas mediciones para mostrar
    measurements = cursor.execute(
        "SELECT id, timestamp, pm2_5, pm10, quality_level FROM measurements ORDER BY id DESC LIMIT 10"
    ).fetchall()
    conn.close()
    
    return render_template('index.html', measurements=measurements)

if __name__ == '__main__':
    app.run(debug=True)