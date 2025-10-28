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

from pathlib import Path
from datetime import datetime
import csv

app = Flask(__name__)


def parse_float(v):
    try:
        return float(v) if v not in ("", None) else None
    except (ValueError, TypeError):
        return None


# Inicializar motor y BDD
engine = AirExpertEngine()
init_db()

# Rutas de CSV
CSV_IN = Path("data/initial_data.csv")
CSV_OUT = Path("data/history.csv")
CSV_OUT_HEADERS = [
    "timestamp",
    "zona",
    "evento_biomasa",
    "quality_level",
    "pm2_5",
    "pm10",
    "no2",
    "o3",
    "so2",
    "co",
    "temp",
    "rh",
    "v_viento",
]


def append_to_csv(medida: dict, condicion: dict, contexto: dict, quality_label: str):
    """Anexa cada evaluación a data/history.csv."""
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().isoformat(timespec="seconds")
    row = {
        "timestamp": now,
        "zona": contexto.get("zona"),
        "evento_biomasa": contexto.get("evento_biomasa"),
        "quality_level": quality_label,
        "pm2_5": medida.get("pm2_5"),
        "pm10": medida.get("pm10"),
        "no2": medida.get("no2"),
        "o3": medida.get("o3"),
        "so2": medida.get("so2"),
        "co": medida.get("co"),
        "temp": condicion.get("temperatura"),
        "rh": condicion.get("humedad"),
        "v_viento": condicion.get("v_viento"),
    }
    write_header = not CSV_OUT.exists()
    with open(CSV_OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_OUT_HEADERS)
        if write_header:
            w.writeheader()
        w.writerow({k: ("" if v is None else v) for k, v in row.items()})


def load_csv_to_db(path: Path = CSV_IN) -> int:
    """Carga data/initial_data.csv → evalúa con el motor → guarda en SQLite."""
    if not path.exists():
        return 0
    count = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = SensorInput(
                PM2_5_24h=parse_float(row.get("PM2_5_24h") or row.get("pm25") or row.get("pm2_5")),
                PM10_24h=parse_float(row.get("PM10_24h") or row.get("pm10")),
                NO2_24h=parse_float(row.get("NO2_24h") or row.get("no2")),
                O3_8h=parse_float(row.get("O3_8h") or row.get("o3")),
                SO2_24h=parse_float(row.get("SO2_24h") or row.get("so2")),
                CO_24h=parse_float(row.get("CO_24h") or row.get("co")),
                temp=parse_float(row.get("temp") or row.get("temperatura")),
                rh=parse_float(row.get("rh") or row.get("humedad")),
            )
            fact = Fact(**to_fact_dict(data))
            res = engine.evaluate(fact)

            medida = {
                "pm2_5": data.PM2_5_24h,
                "pm10": data.PM10_24h,
                "no2": data.NO2_24h,
                "co": data.CO_24h,
                "o3": data.O3_8h,
                "so2": data.SO2_24h,
            }
            condicion = {
                "temperatura": data.temp,
                "humedad": data.rh,
                "v_viento": None,
            }
            contexto = {
                "zona": (row.get("zona") or None),
                "hora": (row.get("hora") or None),
                "evento_biomasa": int(row.get("evento_biomasa") or 0),
                "quality_level": res.label,
            }
            save_full_record(medida, condicion, contexto)
            count += 1
    return count


def export_history_to_csv(path: Path = CSV_OUT, limit: int = 1000) -> int:
    """Exporta el join reciente (SQLite) a CSV_OUT."""
    rows = fetch_recent_context(limit)
    headers = [
        "id",
        "zona",
        "hora",
        "evento_biomasa",
        "quality_level",
        "pm2_5",
        "pm10",
        "no2",
        "co",
        "o3",
        "so2",
        "temperatura",
        "humedad",
        "v_viento",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in rows:
            w.writerow(r)
    return len(rows)


# Autocarga CSV inicial si la BD está vacía
try:
    if not fetch_recent_context(1) and CSV_IN.exists():
        load_csv_to_db(CSV_IN)
except Exception:
    # Evita romper el arranque si falla la ingesta inicial
    pass


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        # Construir SensorInput desde distintos posibles nombres de campo
        data = SensorInput(
            PM2_5_24h=(parse_float(request.form.get("pm25"))
                       or parse_float(request.form.get("pm2_5"))
                       or parse_float(request.form.get("pm2_5_24h"))),
            PM10_24h=(parse_float(request.form.get("pm10"))
                      or parse_float(request.form.get("pm_10"))),
            NO2_24h=parse_float(request.form.get("no2")),
            O3_8h=parse_float(request.form.get("o3")),
            SO2_24h=parse_float(request.form.get("so2")),
            CO_24h=parse_float(request.form.get("co")),
            temp=parse_float(request.form.get("temp")),
            rh=parse_float(request.form.get("rh")),
        )

        # Evaluar con motor experto
        fact = Fact(**to_fact_dict(data))
        result = engine.evaluate(fact)

        # Guardar todo en una sola llamada (medida + condición + contexto)
        zona = request.form.get("zona") or None
        evento = request.form.get("evento_biomasa")
        try:
            evento_val = int(evento) if evento not in (None, "") else 0
        except ValueError:
            evento_val = 0

        medida = {
            "pm2_5": data.PM2_5_24h,
            "pm10": data.PM10_24h,
            "no2": data.NO2_24h,
            "co": data.CO_24h,
            "o": data.O3_8h,  # compatible, pero guardamos como 'o3' más abajo
        }
        medida["o3"] = medida.pop("o", None)
        medida["so2"] = data.SO2_24h

        condicion = {
            "temperatura": data.temp,
            "humedad": data.rh,
            "v_viento": None,
        }
        contexto_extra = {
            "zona": zona,
            "hora": None,
            "evento_biomasa": evento_val,
            "quality_level": result.label,
        }

        save_full_record(medida, condicion, contexto_extra)

        # Guardar también en CSV de historial
        append_to_csv(medida, condicion, contexto_extra, result.label)

        return redirect(url_for("index"))

    # Mostrar historial: contexto reciente (incluye join con medidas/condiciones)
    history = fetch_recent_context(10)
    return render_template("index.html", result=result, history=history)


if __name__ == "__main__":
    app.run(debug=True)