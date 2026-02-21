from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "Byron"  

# Ruta principal: renderiza index.html
@app.get("/")
def index():
    return render_template("index.html")

# Página de especialidades
@app.get("/especialidades")
def especialidades():
    return render_template("especialidades.html")


@app.route("/turno", methods=["GET", "POST"])
def turno_guardar():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        especialidad = request.form.get("especialidad", "").strip()
        fecha = request.form.get("fecha", "").strip()
        hora = request.form.get("hora", "").strip()
        notas = request.form.get("notas", "").strip()

        # Validaciones mínimas
        errores = []
        if not nombre: errores.append("El nombre es obligatorio.")
        if not especialidad: errores.append("La especialidad es obligatoria.")
        if not fecha: errores.append("La fecha es obligatoria.")
        if not hora: errores.append("La hora es obligatoria.")

        if errores:
            for e in errores:
                flash(e, "danger")
            # Re-render con lo escrito y el resumen anterior
            return render_template(
                "turno.html",
                nombre=nombre,
                form_data={"nombre": nombre, "especialidad": especialidad, "fecha": fecha, "hora": hora, "notas": notas},
                turno_actual=session.get("turno_actual"),
            )

        # Guardar en sesión
        session["turno_actual"] = {
            "paciente": nombre,
            "especialidad": especialidad,
            "fecha": fecha,
            "hora": hora,
            "notas": notas,
            "estado": "Disponible",
            "clinica": "SaluVida",
        }
        flash("Turno guardado correctamente.", "success")
        # PRG pattern
        return redirect(url_for("turno_guardar"))

    # GET
    return render_template("turno.html", nombre=None, turno_actual=session.get("turno_actual"))

# Turno con un nombre de paciente en la URL (demo)
@app.get("/turno/<path:nombre>")
def turno(nombre):
    # Muestra la misma vista, iniciando el nombre como placeholder (no guarda)
    return render_template("turno.html", nombre=nombre, turno_actual=session.get("turno_actual"))

# Demostración de turno sin nombre
@app.get("/turno-demo")
def turno_demo():
    return render_template("turno.html", nombre=None, turno_actual=session.get("turno_actual"))

# Médicos por especialidad 
@app.get("/medico/<string:especialidad>")
def medico_por_especialidad(especialidad):
    paciente_simulado = f"Paciente de {especialidad.replace('-', ' ').title()}"
    return render_template("turno.html", nombre=paciente_simulado, turno_actual=session.get("turno_actual"))

# Página "Acerca de"
@app.get("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)