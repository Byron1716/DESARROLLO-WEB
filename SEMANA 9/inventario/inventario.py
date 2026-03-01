from producto import Producto
import sqlite3

class Inventario:
    def __init__(self, db_name="inventario.db"):
        self.db_name = db_name
        self.productos = {}   # colección principal

        self._crear_tabla()
        self._cargar_desde_db()

    def _crear_tabla(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                cantidad INTEGER,
                precio REAL
            )
        """)
        con.commit()
        con.close()

    def _cargar_desde_db(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM productos")
        for id, nombre, cantidad, precio in cur.fetchall():
            self.productos[id] = Producto(id, nombre, cantidad, precio)
        con.close()

    def agregar_producto(self, producto):
        self.productos[producto.id] = producto

        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO productos VALUES (?, ?, ?, ?)",
                    (producto.id, producto.nombre, producto.cantidad, producto.precio))
        
    def eliminar_producto(self, id):
        if id in self.productos:
            del self.productos[id]

            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute("DELETE FROM productos WHERE id = ?", (id,))
            con.commit()
            con.close()
            return True
        return False
    
    def actualizar_producto(self, id, cantidad=None, precio=None):
        if id in self.productos:
            prod = self.productos[id]

            if cantidad is not None:
                prod.set_cantidad(cantidad)
            if precio is not None:
                prod.set_precio(precio)

            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute("""
                UPDATE productos SET cantidad=?, precio=? WHERE id=?
            """, (prod.cantidad, prod.precio, id))
            con.commit()
            con.close()
            return True
        return False
    
    def buscar_por_nombre(self, nombre):
        return [
            p for p in self.productos.values()
            if nombre.lower() in p.nombre.lower()
        ]
    
    def mostrar_todos(self):
        return list(self.productos.values())