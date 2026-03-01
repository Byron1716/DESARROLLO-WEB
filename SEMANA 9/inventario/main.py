from inventario import Inventario
from producto import Producto

inv = Inventario()

def leer_int(mensaje):
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("⚠️  Debes ingresar un número entero. Intenta nuevamente.")

def leer_float(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("⚠️  Debes ingresar un número (usa punto decimal). Intenta nuevamente.")

def menu():
    while True:
        print("\n--- MENU INVENTARIO ---")
        print("1. Agregar producto")
        print("2. Eliminar producto")
        print("3. Actualizar producto")
        print("4. Buscar por nombre")
        print("5. Mostrar inventario")
        print("6. Salir")

        op = input("Seleccione una opción: ").strip()

        if op == "1":
            id = leer_int("ID: ")
            nombre = input("Nombre: ").strip()
            cantidad = leer_int("Cantidad: ")
            precio = leer_float("Precio: ")

            try:
                inv.agregar_producto(Producto(id, nombre, cantidad, precio))
                print("✅ Producto agregado.")
            except Exception as e:
                print(f"❌ No se pudo agregar: {e}")

        elif op == "2":
            id = leer_int("ID del producto a eliminar: ")
            print("✅ Eliminado" if inv.eliminar_producto(id) else "❌ No existe un producto con ese ID.")

        elif op == "3":
            id = leer_int("ID: ")
            cantidad = leer_int("Nueva cantidad: ")
            precio = leer_float("Nuevo precio: ")
            print("✅ Actualizado" if inv.actualizar_producto(id, cantidad, precio) else "❌ No existe un producto con ese ID.")

        elif op == "4":
            nombre = input("Buscar: ").strip()
            resultados = inv.buscar_por_nombre(nombre)
            if resultados:
                # (Opcional) ordenar alfabéticamente por nombre
                resultados = sorted(resultados, key=lambda p: p.get_nombre().lower())
                for p in resultados:
                    print(p)
            else:
                print("ℹ️  No se encontraron productos con ese nombre.")

        elif op == "5":
            productos = inv.mostrar_todos()
            if productos:
                # (Opcional) ordenar por ID
                productos = sorted(productos, key=lambda p: p.get_id())
                for p in productos:
                    print(p)
            else:
                print("ℹ️  El inventario está vacío.")

        elif op == "6":
            print("👋 Saliendo... ¡Hasta luego!")
            break

        else:
            print("⚠️  Opción inválida. Elige una opción del 1 al 6.")

if __name__ == "__main__":
    menu()