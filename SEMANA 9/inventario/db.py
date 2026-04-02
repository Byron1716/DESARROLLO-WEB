# inventario/db.py
import os
import sqlite3
from flask import g

# Ruta de la base de datos (un solo SQLite para todo el proyecto)

DATABASE = r"C:\Users\Byron Rosado\DESARROLLO WEB\SEMANA 9\clinica.db"

def get_db():
    if "db" not in g:
        print("🧠 USANDO BASE:", DATABASE)
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Cierra la conexión SQLite al finalizar la request
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()