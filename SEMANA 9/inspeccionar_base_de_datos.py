import sqlite3, os

DB = "clinica.db"
print("Ruta absoluta:", os.path.abspath(DB))

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("\nTablas:")
for (name,) in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(" -", name)

print("\nPacientes:")
for row in cur.execute("SELECT id, nombre, cedula, telefono, email FROM pacientes ORDER BY id DESC"):
    print(dict(row))

print("\nTurnos:")
for row in cur.execute("""
    SELECT t.id, p.nombre AS paciente, p.cedula, t.especialidad, t.fecha, t.hora, t.estado, t.created_at
      FROM turnos t
      JOIN pacientes p ON p.id = t.paciente_id
  ORDER BY t.id DESC
"""):
    print(dict(row))

con.close()