================================================================================
  ASISTENTE EXPERTO - DETECCIÓN DE CONTAMINACIÓN DEL AIRE
================================================================================

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

2. Abrir terminal y navegar a la carpeta del proyecto:

3. Instalar dependencias Python:

   python -m pip install -r requirements.txt

4. (Opcional) Preparar datos iniciales:
   - Editar data/initial_data.csv con mediciones históricas.
   - La app cargará este CSV automáticamente en SQLite si la base está vacía.

--------------------------------------------------------------------------------
EJECUCIÓN
--------------------------------------------------------------------------------

1. Iniciar el servidor Flask:

   python app.py

2. Abrir el navegador y acceder a:

   http://127.0.0.1:5000/

3. Usar el formulario web

4. Ver resultados

5. Detener el servidor:
   - Presionar Ctrl+C en la terminal.

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

================================================================================