# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
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
        # Campos del formulario (agregaremos 2 nuevos: cedula, telefono/email)
        nombre       = request.form.get("nombre", "").strip()
        cedula       = request.form.get("cedula", "").strip() or None
        telefono     = request.form.get("telefono", "").strip() or None
        email        = request.form.get("email", "").strip() or None
        especialidad = request.form.get("especialidad", "").strip()
        fecha        = request.form.get("fecha", "").strip()
        hora         = request.form.get("hora", "").strip()
        notas        = request.form.get("notas", "").strip()

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
                nombre=nombre,
                form_data={
                    "nombre": nombre, "cedula": cedula, "telefono": telefono, "email": email,
                    "especialidad": especialidad, "fecha": fecha, "hora": hora, "notas": notas
                },
                turno_actual=session.get("turno_actual"),
            )

        # 1) Crear o reutilizar paciente
        paciente_id = upsert_paciente(nombre, cedula, telefono, email)
        # 2) Crear turno
        turno_id = crear_turno(paciente_id, especialidad, fecha, hora, notas)

        # (Opcional) Mantener resumen en sesión para la vista actual
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
        flash("Turno guardado correctamente en la base de datos.", "success")
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)