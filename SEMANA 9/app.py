# app.py
from flask import (Flask, render_template, request, redirect, url_for, session, flash, send_from_directory)
from flask_login import (UserMixin, LoginManager, login_user, logout_user, login_required, current_user)
from werkzeug.security  import generate_password_hash, check_password_hash
import os
import csv
import json
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from flask import send_file
from inventario.inventario import (
    init_db,
    listar_especialidades,
    crear_especialidad,
    obtener_especialidad,
    eliminar_especialidad,
    upsert_paciente,
    crear_turno,
    listar_turnos,
    listar_turnos_reporte
)

from inventario.db import close_db


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.teardown_appcontext
def cerrar_conexion(exception):
    close_db(exception)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['usuario']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect("clinica.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_usuario FROM usuarios WHERE nombre = ?",
            (nombre,)
        )

        if cursor.fetchone():
            conn.close()
            flash("El usuario ya existe, elige otro", "warning")
            return render_template('registro.html')

        cursor.execute(
            "INSERT INTO usuarios (nombre, password) VALUES (?, ?)",
            (nombre, password)
        )

        conn.commit()
        conn.close()

        flash("Usuario registrado correctamente", "success")
        return redirect(url_for('login'))

    return render_template('registro.html')

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("clinica.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id_usuario, nombre, password FROM usuarios WHERE id_usuario = ?",
        (user_id,)
    )
    data = cursor.fetchone()
    conn.close()

    if data:
        return Usuario(data[0], data[1], data[2])
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conn = sqlite3.connect("clinica.db")
        cursor = conn.cursor()

        
        cursor.execute(
            "SELECT id_usuario, nombre, password FROM usuarios WHERE nombre = ?",
            (usuario,)
        )

        data = cursor.fetchone()
        conn.close()

        if data and check_password_hash(data[2], password):
            user = Usuario(data[0], data[1], data[2])
            login_user(user)
            return redirect(url_for('dashboard'))

        # Login fallido
        flash("Usuario o contraseña incorrectos", "danger")
        return render_template('login.html')

    return render_template('login.html')


@app.route('/perfil') 
def perfil(): 
    if current_user.is_authenticated: 
        return f'Bienvenido, {current_user.usuario}' 
    return 'Debes iniciar sesión'

@app.route('/logout') 
def logout(): 
    logout_user() 
    return "Sesión cerrada exitosamente"


class Usuario(UserMixin): 
    def __init__ (self, id_usuario, usuario, password): 
        self.id = id_usuario
        self.usuario = usuario 
        self.password = password


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')


# ---------- Archivos de datos ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TXT_FILE = os.path.join(DATA_DIR, "registros.txt")
JSON_FILE = os.path.join(DATA_DIR, "registros.json")
CSV_FILE = os.path.join(DATA_DIR, "registros.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(TXT_FILE):
    with open(TXT_FILE, "w", encoding="utf-8") as f:
        f.write("")

if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "nombre", "cedula", "telefono", "email",
            "especialidad", "fecha", "hora", "notas", "fecha_iso"
        ])
        writer.writeheader()

# Inicializar BD al cargar la app
with app.app_context():
    init_db()


# ---------- Rutas ----------
@app.get("/")
def index():
    return render_template("login.html")

@app.get("/especialidades")
def especialidades():
    datos = listar_especialidades()
    return render_template("especialidades.html", especialidades=listar_especialidades())

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

        # 3) Guardar en BD
        paciente_id = upsert_paciente(nombre, cedula, telefono, email)
        turno_id = crear_turno(paciente_id, especialidad, fecha, hora, notas)

        # 4) Sesión
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

        # 5) Persistencia en archivos
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

@app.get("/turno-demo")
def turno_demo():
    return redirect(url_for("turno_guardar"))

@app.get("/pacientes")
def ver_pacientes():
    pacientes = listar_pacientes()
    return render_template("pacientes.html", pacientes=pacientes)

@app.get("/reporte/especialidades")
def reporte_especialidades():
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(2 * cm, height - 2 * cm, "Reporte General de Especialidades y Pacientes")

    pdf.setFont("Helvetica", 10)
    y = height - 3.5 * cm

    turnos = listar_turnos_reporte()

    if not turnos:
        pdf.drawString(2 * cm, y, "No existen turnos registrados.")
    else:
        especialidad_actual = None

        for t in turnos:
            # Cambio de especialidad
            if t["especialidad"] != especialidad_actual:
                y -= 1 * cm
                pdf.setFont("Helvetica-Bold", 11)
                pdf.drawString(2 * cm, y, f"Especialidad: {t['especialidad']}")
                y -= 0.6 * cm
                pdf.setFont("Helvetica", 10)
                especialidad_actual = t["especialidad"]

            texto = (
                f"Paciente: {t['paciente']} | "
                f"Cédula: {t['cedula'] or '-'} | "
                f"Tel: {t['telefono'] or '-'} | "
                f"Email: {t['email'] or '-'} | "
                f"Fecha: {t['fecha']} | Hora: {t['hora']} | "
                f"Estado: {t['estado']}"
            )
            pdf.drawString(2.5 * cm, y, texto)
            y -= 0.5 * cm

            if t["notas"]:
                pdf.setFont("Helvetica-Oblique", 9)
                pdf.drawString(3 * cm, y, f"Notas: {t['notas']}")
                y -= 0.5 * cm
                pdf.setFont("Helvetica", 10)

            # Salto de página automático
            if y < 2 * cm:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = height - 2 * cm

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="reporte_especialidades_y_pacientes.pdf",
        mimetype="application/pdf"
    )

@app.route("/agregar_servicio", methods=["GET", "POST"])
def agregar_servicio():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()

        if not nombre:
            flash("El nombre es obligatorio", "danger")
            return render_template("agregar_servicio.html")

        try:
            crear_especialidad(nombre)
            flash("Especialidad agregada correctamente", "success")
            return redirect(url_for("especialidades"))

        except sqlite3.IntegrityError:
            flash("La especialidad ya existe", "warning")
            return render_template("agregar_servicio.html")

    return render_template("agregar_servicio.html")


# Cancelar turno
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

# Descargar archivos
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
        path=filename,               # Flask 3.x usa 'path'
        as_attachment=True,
        download_name=filename
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)