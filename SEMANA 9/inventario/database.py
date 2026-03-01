
import sqlite3

DB_NAME = "clinica.db"

def get_connection():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_connection()
    cur = con.cursor()
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS pacientes (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre   TEXT NOT NULL,
        cedula   TEXT UNIQUE,
        telefono TEXT,
        email    TEXT
    );

    CREATE TABLE IF NOT EXISTS turnos (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id  INTEGER NOT NULL,
        especialidad TEXT NOT NULL,
        fecha        TEXT NOT NULL,     -- ISO: YYYY-MM-DD
        hora         TEXT NOT NULL,     -- HH:MM
        notas        TEXT,
        estado       TEXT NOT NULL DEFAULT 'Programado',
        created_at   TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
    );
    """)
    con.commit()
    con.close()

# --------- CRUD helpers ---------

def upsert_paciente(nombre, cedula=None, telefono=None, email=None):
    con = get_connection()
    cur = con.cursor()
    # Si envías cédula, intentamos reutilizar
    if cedula:
        cur.execute("SELECT id FROM pacientes WHERE cedula = ?", (cedula,))
        row = cur.fetchone()
        if row:
            cur.execute("""
                UPDATE pacientes
                   SET nombre=?, telefono=?, email=?
                 WHERE id=?
            """, (nombre, telefono, email, row["id"]))
            con.commit()
            con.close()
            return row["id"]
    # Si no existe, lo creamos
    cur.execute("""
        INSERT INTO pacientes (nombre, cedula, telefono, email)
        VALUES (?, ?, ?, ?)
    """, (nombre, cedula, telefono, email))
    con.commit()
    pid = cur.lastrowid
    con.close()
    return pid

def crear_turno(paciente_id, especialidad, fecha, hora, notas=None, estado='Programado'):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO turnos (paciente_id, especialidad, fecha, hora, notas, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (paciente_id, especialidad, fecha, hora, notas, estado))
    con.commit()
    turno_id = cur.lastrowid
    con.close()
    return turno_id

def listar_turnos():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT  t.id,
                p.nombre AS paciente,
                p.cedula,
                t.especialidad,
                t.fecha,
                t.hora,
                t.estado
          FROM turnos t
          JOIN pacientes p ON p.id = t.paciente_id
      ORDER BY t.fecha, t.hora
    """)
    rows = cur.fetchall()
    con.close()
    return rows

def listar_pacientes():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT id, nombre, cedula, telefono, email
          FROM pacientes
      ORDER BY nombre
    """)
    rows = cur.fetchall()
    con.close()
    return rows

def obtener_turno(turno_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT  t.*,
                p.nombre   AS paciente,
                p.cedula   AS paciente_cedula,
                p.telefono AS paciente_telefono,
                p.email    AS paciente_email
          FROM turnos t
          JOIN pacientes p ON p.id = t.paciente_id
         WHERE t.id = ?
    """, (turno_id,))
    row = cur.fetchone()
    con.close()
    return row

def actualizar_estado_turno(turno_id, nuevo_estado):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE turnos SET estado=? WHERE id=?", (nuevo_estado, turno_id))
    con.commit()
    con.close()

def eliminar_turno(turno_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM turnos WHERE id=?", (turno_id,))
    con.commit()
    con.close()