# inventario/inventario.py
from inventario.db import get_db

print("✅ INVENTARIO SQLITE CARGADO:", __file__)

# ---------- Init DB ----------


def init_db():
    db = get_db()

    # Tabla especialidades
    db.execute("""
    CREATE TABLE IF NOT EXISTS especialidades (
        id_especialidad INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT,
        icono TEXT DEFAULT 'mdi-stethoscope',
        color TEXT DEFAULT 'primary',
        estado TEXT DEFAULT 'activa',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cedula TEXT,
        telefono TEXT,
        email TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS turnos (
        id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER NOT NULL,
        especialidad TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        notas TEXT,
        estado TEXT DEFAULT 'Programado',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente)
    )
    """)


    db.commit()


# ---------- Especialidades ----------

def crear_paciente(nombre, cedula=None, telefono=None, email=None):
    db = get_db()
    cur = db.execute(
        "INSERT INTO pacientes (nombre, cedula, telefono, email) VALUES (?, ?, ?, ?)",
        (nombre, cedula, telefono, email)
    )
    db.commit()
    return cur.lastrowid

def crear_especialidad(nombre, icono, color):
    db = get_db()
    db.execute(
        "INSERT INTO especialidades (nombre, icono, color) VALUES (?, ?, ?)",
        (nombre, icono, color)
    )
    db.commit()


def listar_especialidades():
    db = get_db()
    return db.execute(
        """
        SELECT
            id,
            nombre,
            icono,
            color
        FROM especialidades
        ORDER BY nombre
        """
    ).fetchall()

def obtener_especialidad(id):
    db = get_db()
    return db.execute(
        "SELECT * FROM especialidades WHERE id = ?",
        (id,)
    ).fetchone()


def eliminar_especialidad(id):
    db = get_db()
    db.execute(
        """
        DELETE FROM especialidades
        WHERE id = ?
        """,
        (id,)
    )
    db.commit()


def upsert_paciente(nombre, cedula=None, telefono=None, email=None):
    db = get_db()

    if cedula:
        cur = db.execute(
            "SELECT id_paciente FROM pacientes WHERE cedula = ?",
            (cedula,)
        )
        row = cur.fetchone()
        if row:
            return row["id_paciente"]

    if email and not cedula:
        cur = db.execute(
            "SELECT id_paciente FROM pacientes WHERE email = ?",
            (email,)
        )
        row = cur.fetchone()
        if row:
            return row["id_paciente"]

    cur = db.execute(
        """
        INSERT INTO pacientes (nombre, cedula, telefono, email)
        VALUES (?, ?, ?, ?)
        """,
        (nombre, cedula, telefono, email)
    )
    db.commit()
    return cur.lastrowid

def crear_turno(id_paciente, especialidad, fecha, hora, notas=None):
    db = get_db()
    cur = db.execute(
        """
        INSERT INTO turnos (id_paciente, especialidad, fecha, hora, notas)
        VALUES (?, ?, ?, ?, ?)
        """,
        (id_paciente, especialidad, fecha, hora, notas)
    )
    db.commit()
    return cur.lastrowid

def listar_turnos():
    db = get_db()
    cur = db.execute("""
        SELECT
            t.id_turno,
            t.fecha,
            t.hora,
            t.estado,
            t.notas,
            p.nombre AS paciente,
            t.especialidad
        FROM turnos t
        JOIN pacientes p ON p.id_paciente = t.id_paciente
        ORDER BY t.fecha DESC, t.hora DESC
    """)
    return cur.fetchall()


def listar_turnos_reporte():
    db = get_db()
    cur = db.execute("""
        SELECT
            t.especialidad,
            p.nombre AS paciente,
            p.cedula,
            p.telefono,
            p.email,
            t.fecha,
            t.hora,
            t.estado,
            t.notas
        FROM turnos t
        JOIN pacientes p ON p.id_paciente = t.id_paciente
        ORDER BY t.especialidad, t.fecha, t.hora
    """)
    return cur.fetchall()

def actualizar_especialidad(id, nombre, icono, color):
    db = get_db()
    db.execute(
        """
        UPDATE especialidades
        SET nombre = ?, icono = ?, color = ?
        WHERE id = ?
        """,
        (nombre, icono, color, id)
    )
    db.commit()

