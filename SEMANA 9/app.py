from flask import Flask, render_template
import os

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/especialidades")
def especialidades():
    return render_template("especialidades.html")

@app.get("/turno/<path:nombre>")
def turno(nombre):
    return render_template("turno.html", nombre=nombre)

@app.get("/turno-demo")
def turno_demo():
    return render_template("turno.html", nombre=None)

@app.get("/medico/<path:especialidad>")
def medico_por_especialidad(especialidad):
    # Aquí luego listamos médicos según especialidad
    return render_template("turno.html", nombre=f"Paciente{especialidad.replace('-', ' ').title()}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)