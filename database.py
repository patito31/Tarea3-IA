import sqlite3

DB_NAME = 'air_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabla de mediciones de contaminantes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pm2_5 REAL,
            pm10 REAL,
            no2 REAL,
            co REAL,
            o3 REAL,
            so2 REAL
        );
    ''')

    # Tabla de condiciones meteorológicas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS condiciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperatura REAL,
            humedad REAL,
            v_viento REAL
        );
    ''')

    # Tabla de contexto (sin columna zona)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contexto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hora DATETIME,
            evento_biomasa INTEGER NOT NULL DEFAULT 0,
            quality_level TEXT,
            medida_id INTEGER,
            condicion_id INTEGER,
            FOREIGN KEY (medida_id) REFERENCES medidas(id) ON DELETE CASCADE,
            FOREIGN KEY (condicion_id) REFERENCES condiciones(id) ON DELETE CASCADE
        );
    ''')

    conn.commit()
    conn.close()


def save_measurement(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medidas (pm2_5, pm10, no2, co, o3, so2)
        VALUES (:pm2_5, :pm10, :no2, :co, :o3, :so2)
    ''', data)
    conn.commit()
    conn.close()


def save_condition(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO condiciones (temperatura, humedad, v_viento)
        VALUES (:temperatura, :humedad, :v_viento)
    ''', data)
    conn.commit()
    conn.close()


def save_context(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contexto (hora, evento_biomasa, quality_level, medida_id, condicion_id)
        VALUES (:hora, :evento_biomasa, :quality_level, :medida_id, :condicion_id)
    ''', data)
    conn.commit()
    conn.close()
