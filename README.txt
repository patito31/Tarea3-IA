================================================================================
  ASISTENTE EXPERTO - DETECCIÓN DE CONTAMINACIÓN DEL AIRE
================================================================================

Sistema experto basado en reglas para evaluar la calidad del aire mediante
concentraciones de contaminantes (PM2.5, PM10, NO2, O3, SO2, CO) y condiciones
ambientales (temperatura, humedad relativa).

--------------------------------------------------------------------------------
ARQUITECTURA DEL SISTEMA
--------------------------------------------------------------------------------

[Datos CSV] 
    ↓
[Módulo de Adquisición] ← recibe datos del formulario web y los valida
    ↓
[BDD SQLite] ← almacena registros de contaminación y umbrales
    ↓
[Motor de Inferencia] ← analiza las mediciones según reglas OMS
    ↓
[Interfaz Flask] ← visualiza resultados, alertas y recomendaciones

--------------------------------------------------------------------------------
COMPONENTES PRINCIPALES
--------------------------------------------------------------------------------

• app.py
  Aplicación Flask (backend Python). Gestiona el formulario web, ejecuta el
  motor de inferencia y guarda resultados en SQLite y CSV.

• inference_engine.py
  Motor de inferencia basado en reglas. Calcula AQI (PM2.5), compara con
  umbrales OMS y genera etiquetas (Buena, Moderada, Riesgo moderado/alto).

• acquisition_module.py
  Módulo de adquisición. Define el modelo SensorInput (Pydantic) para validar
  entradas de contaminantes y condiciones ambientales.

• database.py
  Helpers de base de datos. Tablas normalizadas (medidas, condiciones, contexto)
  con función save_full_record() para insertar en una sola transacción.

• templates/index.html
  Interfaz web (Jinja2). Formulario para ingresar datos, tarjeta con resultados
  y tabla de historial con badges de color según nivel de riesgo.

• data/air_rules.json
  Base de conocimiento: umbrales OMS y recomendaciones por nivel de calidad.

• data/initial_data.csv
  Datos iniciales (opcional). Se cargan automáticamente en SQLite al iniciar
  la app si la base está vacía.

• data/history.csv
  Historial exportado. Cada evaluación se anexa automáticamente.

• data/air_data.db
  Base de datos SQLite (generada automáticamente al ejecutar app.py).

--------------------------------------------------------------------------------
REQUISITOS DE SOFTWARE
--------------------------------------------------------------------------------

• Python 3.10 o superior
• Dependencias Python (ver requirements.txt):
  - flask
  - pydantic

--------------------------------------------------------------------------------
INSTALACIÓN Y CONFIGURACIÓN
--------------------------------------------------------------------------------

1. Clonar o descargar el repositorio en tu máquina local.

2. Abrir PowerShell (o terminal) y navegar a la carpeta del proyecto:

   Set-Location 'C:\Users\joako\Downloads\Tarea3-IA'

3. Instalar dependencias Python:

   python -m pip install -r requirements.txt

   (Si usas un entorno virtual, actívalo antes de ejecutar pip install.)

4. (Opcional) Preparar datos iniciales:
   - Editar data/initial_data.csv con mediciones históricas.
   - La app cargará este CSV automáticamente en SQLite si la base está vacía.

5. Verificar que data/air_rules.json existe y es JSON válido (sin comentarios).

--------------------------------------------------------------------------------
EJECUCIÓN
--------------------------------------------------------------------------------

1. Iniciar el servidor Flask:

   python app.py

2. Abrir el navegador y acceder a:

   http://127.0.0.1:5000/

3. Usar el formulario web:
   - Seleccionar Zona (Centro, Norte, Sur, Este, Oeste).
   - Indicar si hay Evento de biomasa (No / Sí).
   - Ingresar valores de contaminantes (µg/m³) y condiciones ambientales.
   - Hacer clic en "Evaluar Calidad del Aire".

4. Ver resultados:
   - Tarjeta con nivel de calidad (Buena, Moderada, Riesgo moderado, Riesgo alto).
   - AQI PM2.5, explicación, alertas y recomendaciones.
   - Tabla de historial con badges de color por nivel.

5. Detener el servidor:
   - Presionar Ctrl+C en la terminal.

--------------------------------------------------------------------------------
ESTRUCTURA DE DATOS
--------------------------------------------------------------------------------

TABLA medidas (SQLite):
  - id, timestamp, pm2_5, pm10, no2, co, o3, so2

TABLA condiciones (SQLite):
  - id, temperatura, humedad, v_viento

TABLA contexto (SQLite):
  - id, zona, hora, evento_biomasa, quality_level, medida_id, condicion_id

CSV initial_data.csv (columnas):
  zona, hora, evento_biomasa, PM2_5_24h, PM10_24h, NO2_24h, O3_8h, SO2_24h, 
  CO_24h, temp, rh

CSV history.csv (columnas):
  timestamp, zona, evento_biomasa, quality_level, pm2_5, pm10, no2, o3, so2, 
  co, temp, rh, v_viento

--------------------------------------------------------------------------------
FUNCIONES CLAVE
--------------------------------------------------------------------------------

• save_full_record(medida, condicion, contexto_extra)
  Guarda medición, condición y contexto en una sola transacción (database.py).

• load_csv_to_db(path)
  Carga data/initial_data.csv → evalúa con motor → guarda en SQLite (app.py).

• append_to_csv(medida, condicion, contexto, quality_label)
  Anexa cada evaluación a data/history.csv (app.py).

• engine.evaluate(fact)
  Recibe un objeto Fact, calcula AQI, compara con umbrales OMS y devuelve
  InferenceResult (inference_engine.py).

--------------------------------------------------------------------------------
SOLUCIÓN DE PROBLEMAS
--------------------------------------------------------------------------------

1. Error "ModuleNotFoundError: No module named 'flask'"
   → Instalar dependencias: python -m pip install -r requirements.txt

2. Error "No module named 'pydantic'"
   → Instalar pydantic: python -m pip install pydantic

3. Ves llaves {{ ... }} o {% ... %} en el navegador
   → No abras templates/index.html directamente con file://
   → Ejecuta python app.py y accede a http://127.0.0.1:5000/

4. Error JSON al cargar air_rules.json
   → Verifica que el archivo no contenga comentarios (// o /* */)
   → Debe ser JSON válido puro.

5. La tabla de historial está vacía
   → Ingresa al menos una evaluación desde el formulario.
   → Si quieres datos iniciales, edita data/initial_data.csv y reinicia la app.

6. Archivos .pyc en __pycache__
   → Son bytecode compilado (normales). No editar ni abrir como texto.
   → Para limpiar: Remove-Item '__pycache__\*' -Force

--------------------------------------------------------------------------------
CONFIGURACIÓN AVANZADA
--------------------------------------------------------------------------------

• Cambiar puerto del servidor Flask:
  Editar app.py línea final:
    app.run(debug=True, port=8080)

• Añadir más zonas:
  Editar templates/index.html, sección <select name="zona">.

• Personalizar umbrales OMS:
  Editar data/air_rules.json, sección "umbrales_OMS".

• Personalizar recomendaciones:
  Editar data/air_rules.json, sección "recomendaciones".

• Exportar historial completo a CSV:
  Desde Python:
    from app import export_history_to_csv
    export_history_to_csv(limit=1000)

--------------------------------------------------------------------------------
REFERENCIAS
--------------------------------------------------------------------------------

• Directrices OMS sobre calidad del aire (2021):
  https://www.who.int/news-room/feature-stories/detail/what-are-the-who-air-quality-guidelines

• Flask documentation:
  https://flask.palletsprojects.com/

• Pydantic documentation:
  https://docs.pydantic.dev/

--------------------------------------------------------------------------------
CONTACTO Y SOPORTE
--------------------------------------------------------------------------------

Repositorio: https://github.com/patito31/Tarea3-IA
Rama actual: main / Joaco

================================================================================
