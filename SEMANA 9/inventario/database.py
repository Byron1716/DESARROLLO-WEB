# inventario/database.py
import os
import sqlite3
from contextlib import contextmanager

# ----- Ubicación de la BD (clinica.db) -----
# Este archivo está dentro de inventario/, por eso subimos un nivel hasta la raíz del proyecto.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(ROOT_DIR, "clinica.db")

# ----- Conexión -----
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_cursor():
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

# ----- Inicialización de tablas -----
def init_db():
    with db_cursor() as cur:
        # Tabla de pacientes
        cur.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT UNIQUE,         -- opcional única
            telefono TEXT,
            email TEXT
        )
        """)

        # Tabla de especialidades
        cur.execute("""
        CREATE TABLE IF NOT EXISTS especialidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        )
        """)

        # Tabla de turnos (citas)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            especialidad_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,   -- 'YYYY-MM-DD'
            hora TEXT NOT NULL,    -- 'HH:MM'
            notas TEXT,
            estado TEXT NOT NULL DEFAULT 'Programado',
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
            FOREIGN KEY (especialidad_id) REFERENCES especialidades(id) ON DELETE RESTRICT
        )
        """)

    # Semilla de especialidades (si está vacío)
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM especialidades")
        if cur.fetchone()["c"] == 0:
            cur.executemany(
                "INSERT INTO especialidades (nombre) VALUES (?)",
                [(n,) for n in [
                    "Medicina General", "Odontología", "Pediatría", "Ginecología",
                    "Laboratorio", "Traumatología", "Cardiología"
                ]]
            )

# ============================
#       PACIENTES (CRUD)
# ============================
def upsert_paciente(nombre, cedula=None, telefono=None, email=None):
    """
    Inserta o actualiza si existe por cédula.
    Retorna el id del paciente.
    """
    if cedula:
        with db_cursor() as cur:
            cur.execute("SELECT id FROM pacientes WHERE cedula = ?", (cedula,))
            row = cur.fetchone()
            if row:
                cur.execute("""
                    UPDATE pacientes
                    SET nombre = ?, telefono = ?, email = ?
                    WHERE id = ?
                """, (nombre, telefono, email, row["id"]))
                return row["id"]

    # Insertar nuevo
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO pacientes (nombre, cedula, telefono, email)
            VALUES (?, ?, ?, ?)
        """, (nombre, cedula, telefono, email))
        return cur.lastrowid

def crear_paciente(nombre, cedula=None, telefono=None, email=None):
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO pacientes (nombre, cedula, telefono, email)
            VALUES (?, ?, ?, ?)
        """, (nombre, cedula, telefono, email))
        return cur.lastrowid

def listar_pacientes():
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, nombre, cedula, telefono, email
            FROM pacientes
            ORDER BY id DESC
        """)
        return [dict(r) for r in cur.fetchall()]

def obtener_paciente(paciente_id):
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, nombre, cedula, telefono, email
            FROM pacientes
            WHERE id = ?
        """, (paciente_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def actualizar_paciente(paciente_id, nombre, cedula=None, telefono=None, email=None):
    with db_cursor() as cur:
        cur.execute("""
            UPDATE pacientes
            SET nombre = ?, cedula = ?, telefono = ?, email = ?
            WHERE id = ?
        """, (nombre, cedula, telefono, email, paciente_id))
        return cur.rowcount > 0

def eliminar_paciente(paciente_id):
    with db_cursor() as cur:
        cur.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        return cur.rowcount > 0

# ============================
#    ESPECIALIDADES (CRUD)
# ============================
def crear_especialidad(nombre):
    with db_cursor() as cur:
        cur.execute("INSERT INTO especialidades (nombre) VALUES (?)", (nombre,))
        return cur.lastrowid

def listar_especialidades():
    with db_cursor() as cur:
        cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre")
        return [dict(r) for r in cur.fetchall()]

def obtener_especialidad(especialidad_id):
    with db_cursor() as cur:
        cur.execute("SELECT id, nombre FROM especialidades WHERE id = ?", (especialidad_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def actualizar_especialidad(especialidad_id, nombre):
    with db_cursor() as cur:
        cur.execute("UPDATE especialidades SET nombre = ? WHERE id = ?", (nombre, especialidad_id))
        return cur.rowcount > 0

def eliminar_especialidad(especialidad_id):
    with db_cursor() as cur:
        cur.execute("DELETE FROM especialidades WHERE id = ?", (especialidad_id,))
        return cur.rowcount > 0

# ============================
#         TURNOS (CRUD)
# ============================
def crear_turno(paciente_id, especialidad_id, fecha, hora, notas=None):
    with db_cursor() as cur:
        cur.execute("""
            INSERT INTO turnos (paciente_id, especialidad_id, fecha, hora, notas)
            VALUES (?, ?, ?, ?, ?)
        """, (paciente_id, especialidad_id, fecha, hora, notas))
        return cur.lastrowid

def listar_turnos():
    with db_cursor() as cur:
        cur.execute("""
            SELECT
                t.id,
                t.fecha,
                t.hora,
                t.notas,
                t.estado,
                p.nombre   AS paciente,
                p.cedula   AS paciente_cedula,
                e.nombre   AS especialidad
            FROM turnos t
            JOIN pacientes p     ON p.id = t.paciente_id
            JOIN especialidades e ON e.id = t.especialidad_id
            ORDER BY t.fecha DESC, t.hora DESC, t.id DESC
        """)
        return [dict(r) for r in cur.fetchall()]

def obtener_turno(turno_id):
    with db_cursor() as cur:
        cur.execute("""
            SELECT
                t.id, t.paciente_id, t.especialidad_id, t.fecha, t.hora, t.notas, t.estado
            FROM turnos t
            WHERE t.id = ?
        """, (turno_id,))
        row = cur.fetchone()
        return dict(row) if row else None

def actualizar_turno(turno_id, paciente_id, especialidad_id, fecha, hora, notas, estado):
    with db_cursor() as cur:
        cur.execute("""
            UPDATE turnos
            SET paciente_id = ?, especialidad_id = ?, fecha = ?, hora = ?, notas = ?, estado = ?
            WHERE id = ?
        """, (paciente_id, especialidad_id, fecha, hora, notas, estado, turno_id))
        return cur.rowcount > 0

def actualizar_estado_turno(turno_id, nuevo_estado):
    with db_cursor() as cur:
        cur.execute("UPDATE turnos SET estado = ? WHERE id = ?", (nuevo_estado, turno_id))
        return cur.rowcount > 0

def eliminar_turno(turno_id):
    with db_cursor() as cur:
        cur.execute("DELETE FROM turnos WHERE id = ?", (turno_id,))
        return cur.rowcount > 0