# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
import csv
import json
from datetime import datetime
from inventario.database import (
    init_db, upsert_paciente, crear_turno,
    listar_turnos, listar_pacientes,
    obtener_turno, actualizar_estado_turno, eliminar_turno
)

app = Flask(__name__)
app.secret_key = "Byron"

# Inicializar BD al cargar la app
init_db()

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/especialidades")
def especialidades():
    return render_template("especialidades.html")

@app.route("/turno", methods=["GET", "POST"])
def turno_guardar():
    if request.method == "POST":
        # 1) Obtener campos
        nombre = request.form.get("nombre", "").strip()
        cedula = request.form.get("cedula", "").strip() or None
        telefono = request.form.get("telefono", "").strip() or None
        email = request.form.get("email", "").strip() or None
        especialidad = request.form.get("especialidad", "").strip()
        fecha = request.form.get("fecha", "").strip()
        hora = request.form.get("hora", "").strip()
        notas = request.form.get("notas", "").strip()

        # 2) Validación
        errores = []
        if not nombre: errores.append("El nombre es obligatorio.")
        if not especialidad: errores.append("La especialidad es obligatoria.")
        if not fecha: errores.append("La fecha es obligatoria.")
        if not hora: errores.append("La hora es obligatoria.")

        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template(
                "turno.html",
                form_data={
                    "nombre": nombre, "cedula": cedula, "telefono": telefono, "email": email,
                    "especialidad": especialidad, "fecha": fecha, "hora": hora, "notas": notas
                },
                turno_actual=session.get("turno_actual"),
            )

        # 3) Guardar en BD (ANTES de cualquier return del camino exitoso)
        paciente_id = upsert_paciente(nombre, cedula, telefono, email)
        turno_id = crear_turno(paciente_id, especialidad, fecha, hora, notas)

        # 4) Sesión (para tu resumen)
        session["turno_actual"] = {
            "id": turno_id,
            "paciente": nombre,
            "especialidad": especialidad,
            "fecha": fecha,
            "hora": hora,
            "notas": notas,
            "estado": "Programado",
            "clinica": "SaluVida",
        }

        # 5) Persistencia en archivos (TXT/JSON/CSV)
        from datetime import datetime
        import json, csv

        fecha_iso = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        registro = {
            "nombre": nombre or "",
            "cedula": cedula or "",
            "telefono": telefono or "",
            "email": email or "",
            "especialidad": especialidad or "",
            "fecha": fecha or "",
            "hora": hora or "",
            "notas": notas or "",
            "fecha_iso": fecha_iso
        }

        # TXT
        linea_txt = (
            f"Nombre: {registro['nombre']} | Cédula: {registro['cedula']} | "
            f"Teléfono: {registro['telefono']} | Email: {registro['email']} | "
            f"Especialidad: {registro['especialidad']} | Fecha: {registro['fecha']} | "
            f"Hora: {registro['hora']} | Notas: {registro['notas']} | "
            f"FechaRegistro: {registro['fecha_iso']}\n"
        )
        with open(TXT_FILE, "a", encoding="utf-8") as f:
            f.write(linea_txt)

        # JSON
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            lista = json.load(f)
        lista.append(registro)
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)

        # CSV
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "nombre", "cedula", "telefono", "email",
                "especialidad", "fecha", "hora", "notas", "fecha_iso"
            ])
            writer.writerow(registro)

        # 6) Mensaje y redirección 
        flash("Turno guardado en la base y en TXT/JSON/CSV.", "success")
        return redirect(url_for("ver_turnos"))

    # GET
    return render_template("turno.html", nombre=None, turno_actual=session.get("turno_actual"))

# Listado de turnos
@app.get("/turno-demo")
def turno_demo():
    return redirect(url_for("turno_guardar"))


# Listado de pacientes
@app.get("/pacientes")
def ver_pacientes():
    pacientes = listar_pacientes()
    return render_template("pacientes.html", pacientes=pacientes)

# Cancelar turno (cambia estado)
@app.post("/turno/<int:turno_id>/cancelar")
def cancelar_turno(turno_id):
    actualizar_estado_turno(turno_id, "Cancelado")
    flash("Turno cancelado.", "warning")
    return redirect(url_for("ver_turnos"))

# Eliminar turno
@app.post("/turno/<int:turno_id>/eliminar")
def borrar_turno(turno_id):
    eliminar_turno(turno_id)
    flash("Turno eliminado.", "info")
    return redirect(url_for("ver_turnos"))


@app.get("/medico/<string:especialidad>")
def medico_por_especialidad(especialidad):
    paciente_simulado = f"Paciente de {especialidad.replace('-', ' ').title()}"
    return render_template("turno.html", nombre=paciente_simulado, turno_actual=session.get("turno_actual"))

@app.get("/turnos")
def ver_turnos():
    turnos = listar_turnos()
    return render_template("turno.html", turnos=turnos)

@app.get("/about")
def about():
    return render_template("about.html")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TXT_FILE = os.path.join(DATA_DIR, "registros.txt")
JSON_FILE = os.path.join(DATA_DIR, "registros.json")
CSV_FILE = os.path.join(DATA_DIR, "registros.csv")

os.makedirs(DATA_DIR, exist_ok=True)


if not os.path.exists(TXT_FILE):
    with open(TXT_FILE, "w", encoding="utf-8") as f:
        f.write("")  # archivo vacío

if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "nombre", "cedula", "telefono", "email",
            "especialidad", "fecha", "hora", "notas", "fecha_iso"])
        writer.writeheader()

@app.get("/datos/<formato>")
def ver_datos(formato):
    formato = (formato or "").lower().strip()
    if formato == "txt":
        with open(TXT_FILE, "r", encoding="utf-8") as f:
            contenido = f.read()
        return render_template("datos.html", formato="txt", contenido=contenido, registros=None)

    elif formato == "json":
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            registros = json.load(f)
        return render_template("datos.html", formato="json", contenido=None, registros=registros)

    elif formato == "csv":
        filas = []
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            filas.extend(reader)
        return render_template("datos.html", formato="csv", contenido=None, registros=filas)

    else:
        flash("Formato no soportado. Usa txt, json o csv.", "danger")
        return redirect(url_for("index"))


# ---------- Rutas para descargar archivos ----------

@app.route("/descargar/<formato>")
def descargar(formato):
    formato = formato.lower()
    if formato == "txt":
        filename = os.path.basename(TXT_FILE)
    elif formato == "json":
        filename = os.path.basename(JSON_FILE)
    elif formato == "csv":
        filename = os.path.basename(CSV_FILE)
    else:
        flash("Formato no soportado. Usa txt, json o csv.", "error")
        return redirect(url_for("index"))

    return send_from_directory(
        directory=DATA_DIR,
        path=filename,
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)