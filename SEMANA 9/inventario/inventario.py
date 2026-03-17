import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

load_dotenv()

CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "clinica_db"),
    auth_plugin="mysql_native_password",
)

pool = pooling.MySQLConnectionPool(pool_name="pool_clinica", pool_size=5, **CONFIG)

def _conn():
    return pool.get_connection()

def _exec(sql, params=None, many=False, commit=False, dictionary=False):
    conn = _conn()
    try:
        cur = conn.cursor(dictionary=dictionary)
        if many and isinstance(params, list):
            cur.executemany(sql, params)
        else:
            cur.execute(sql, params or ())
        if commit:
            conn.commit()
            return cur.rowcount
        return cur
    except Exception:
        conn.rollback()
        raise
    finally:
        # ojo: NO cerrar cursor aquí si retornamos resultados
        pass

# ---------- Init DB ----------
def init_db():
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS {} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(CONFIG["database"]))
        cur.execute("USE {}".format(CONFIG["database"]))

        cur.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id_paciente INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            cedula VARCHAR(20) UNIQUE,
            telefono VARCHAR(30),
            email VARCHAR(120),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS especialidades (
            id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(120) NOT NULL UNIQUE,
            estado ENUM('activa','inactiva') NOT NULL DEFAULT 'activa',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS turnos (
            id_turno INT AUTO_INCREMENT PRIMARY KEY,
            id_paciente INT NOT NULL,
            especialidad VARCHAR(120) NOT NULL,
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
            notas TEXT,
            estado ENUM('Programado','Atendido','Cancelado') NOT NULL DEFAULT 'Programado',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_turno_paciente FOREIGN KEY (id_paciente)
                REFERENCES pacientes(id_paciente) ON DELETE RESTRICT ON UPDATE CASCADE
        ) ENGINE=InnoDB;
        """)
        conn.commit()
    finally:
        cur.close()
        conn.close()

# ---------- Pacientes ----------
def crear_paciente(nombre, cedula=None, telefono=None, email=None):
    sql = "INSERT INTO pacientes (nombre, cedula, telefono, email) VALUES (%s,%s,%s,%s)"
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, (nombre, cedula, telefono, email))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

def listar_pacientes():
    cur = _exec("SELECT * FROM pacientes ORDER BY id_paciente DESC", dictionary=True)
    rows = cur.fetchall()
    cur.close(); cur.connection.close()
    return rows

def obtener_paciente(id_paciente):
    cur = _exec("SELECT * FROM pacientes WHERE id_paciente=%s", (id_paciente,), dictionary=True)
    row = cur.fetchone()
    cur.close(); cur.connection.close()
    return row

def actualizar_paciente(id_paciente, nombre, cedula=None, telefono=None, email=None):
    sql = "UPDATE pacientes SET nombre=%s, cedula=%s, telefono=%s, email=%s WHERE id_paciente=%s"
    return _exec(sql, (nombre, cedula, telefono, email, id_paciente), commit=True)

def eliminar_paciente(id_paciente):
    return _exec("DELETE FROM pacientes WHERE id_paciente=%s", (id_paciente,), commit=True)

def upsert_paciente(nombre, cedula=None, telefono=None, email=None):
    """
    Si existe por cédula o email, devuelve el id; sino inserta.
    """
    if cedula:
        cur = _exec("SELECT id_paciente FROM pacientes WHERE cedula=%s", (cedula,), dictionary=True)
        row = cur.fetchone(); cur.close(); cur.connection.close()
        if row: return row["id_paciente"]

    if email and not cedula:
        cur = _exec("SELECT id_paciente FROM pacientes WHERE email=%s", (email,), dictionary=True)
        row = cur.fetchone(); cur.close(); cur.connection.close()
        if row: return row["id_paciente"]

    return crear_paciente(nombre, cedula, telefono, email)

# ---------- Especialidades ----------
def listar_especialidades():
    cur = _exec("SELECT * FROM especialidades WHERE estado='activa' ORDER BY nombre", dictionary=True)
    rows = cur.fetchall(); cur.close(); cur.connection.close()
    return rows

def crear_especialidad(nombre, estado="activa"):
    return _exec("INSERT INTO especialidades (nombre, estado) VALUES (%s,%s)", (nombre, estado), commit=True)

def obtener_especialidad(id_especialidad):
    cur = _exec("SELECT * FROM especialidades WHERE id_especialidad=%s", (id_especialidad,), dictionary=True)
    row = cur.fetchone(); cur.close(); cur.connection.close()
    return row

def actualizar_especialidad(id_especialidad, nombre=None, estado=None):
    sets, params = [], []
    if nombre is not None:
        sets.append("nombre=%s"); params.append(nombre)
    if estado is not None:
        sets.append("estado=%s"); params.append(estado)
    params.append(id_especialidad)
    sql = f"UPDATE especialidades SET {', '.join(sets)} WHERE id_especialidad=%s"
    return _exec(sql, tuple(params), commit=True)

def eliminar_especialidad(id_especialidad):
    return _exec("DELETE FROM especialidades WHERE id_especialidad=%s", (id_especialidad,), commit=True)

# ---------- Turnos ----------
def crear_turno(id_paciente, especialidad, fecha, hora, notas=None):
    sql = "INSERT INTO turnos (id_paciente, especialidad, fecha, hora, notas) VALUES (%s,%s,%s,%s,%s)"
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, (id_paciente, especialidad, fecha, hora, notas))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

def listar_turnos():
    sql = """
    SELECT t.id_turno, t.especialidad, t.fecha, t.hora, t.estado, t.notas,
           p.id_paciente, p.nombre AS paciente, p.cedula, p.telefono, p.email
    FROM turnos t
    JOIN pacientes p ON p.id_paciente = t.id_paciente
    ORDER BY t.id_turno DESC
    """
    cur = _exec(sql, dictionary=True)
    rows = cur.fetchall(); cur.close(); cur.connection.close()
    return rows

def obtener_turno(id_turno):
    cur = _exec("SELECT * FROM turnos WHERE id_turno=%s", (id_turno,), dictionary=True)
    row = cur.fetchone(); cur.close(); cur.connection.close()
    return row

def actualizar_turno(id_turno, especialidad=None, fecha=None, hora=None, notas=None):
    sets, params = [], []
    if especialidad is not None:
        sets.append("especialidad=%s"); params.append(especialidad)
    if fecha is not None:
        sets.append("fecha=%s"); params.append(fecha)
    if hora is not None:
        sets.append("hora=%s"); params.append(hora)
    if notas is not None:
        sets.append("notas=%s"); params.append(notas)
    params.append(id_turno)
    sql = f"UPDATE turnos SET {', '.join(sets)} WHERE id_turno=%s"
    return _exec(sql, tuple(params), commit=True)

def actualizar_estado_turno(id_turno, estado):
    return _exec("UPDATE turnos SET estado=%s WHERE id_turno=%s", (estado, id_turno), commit=True)

def eliminar_turno(id_turno):
    return _exec("DELETE FROM turnos WHERE id_turno=%s", (id_turno,), commit=True)