# inventario/db.py
import os
import sqlite3
from flask import g

# Ruta de la base de datos (un solo SQLite para todo el proyecto)

DATABASE = r"C:\Users\Byron Rosado\DESARROLLO WEB\SEMANA 9\clinica.db"

# inventario/db.py
import os
import sqlite3
from flask import g, current_app

def get_db():
    if "db" not in g:
        # ✅ Ruta PORTABLE (Windows, Linux, Render)
        db_path = os.path.join(current_app.root_path, "clinica.db")
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Cierra la conexión SQLite al finalizar la request
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

def close_db(e=None):
    """
    Cierra la conexión SQLite al finalizar la request
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()