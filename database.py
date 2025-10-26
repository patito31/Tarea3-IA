import sqlite3

DB_NAME = 'air_data.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medidas (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pm2_5 REAL,
            pm10 REAL,
            no2 REAL,
            co REAL,
            o3 REAL,
            so2 REAL,       
            
        );
    ''')               

    cursor.execute('''               
        CREATE TABLE IF NOT EXISTS condiciones (
            id INTEGER PRIMARY KEY,
            temperatura REAL,
            humedad REAL,
            v_viento REAL,
       );
    ''')   

    cursor.execute('''   
        CREATE TABLE IF NOT EXISTS contexto (
            id INTEGER PRIMARY KEY,
            zona TEXT,
            hora DATETIME,
            evento_biomasa INTEGER NOT NULL DEFAULT 0,   # 1 si hay presencia de incendio o quema
            quality_level TEXT
                   
            medida_id INTEGER,
            condicion_id INTEGER,      

            FOREIGN KEY (medida_id) REFERENCES medidas(id) ON DELETE CASCADE,
            FOREIGN KEY (condicion_id) REFERENCES condiciones(id) ON DELETE CASCADE
);               
        );                      

    ''')
    conn.commit()
    conn.close()

def save_measurement(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = f"""
        INSERT INTO medidas (pm2_5, pm10, no2, co, o3, so2)
        VALUES (:pm2_5, :pm10, :no2, :co, :o3, :so2)
    """
    cursor.execute(query, data)
    conn.commit()
    conn.close()
    