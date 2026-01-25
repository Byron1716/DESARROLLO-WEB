// --- Persistencia ---
const STORAGE_KEY = "productos_v1";

// Carga desde localStorage o usa un arreglo inicial
function cargarProductos() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const arr = JSON.parse(raw);
      if (Array.isArray(arr)) return arr;
    }
  } catch (e) {
    console.warn("No se pudo leer localStorage:", e);
  }
  // Arreglo inicial por defecto (si no hay nada guardado)
  return [
    { nombre: "Mouse óptico", precio: 12.99, descripcion: "Mouse USB 1200 DPI" },
    { nombre: "Teclado mecánico", precio: 45.5, descripcion: "Switches azules" },
    { nombre: "Audífonos", precio: 25.0, descripcion: "Aislación de ruido" },
  ];
}

function guardarProductos() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(productos));
  } catch (e) {
    console.warn("No se pudo guardar en localStorage:", e);
  }
}

// --- Estado en memoria ---
let productos = cargarProductos();
// Índice del elemento en edición (o null si no hay)
let editIndex = null;

// --- DOM ---
const ulLista = document.getElementById("lista-productos");
const inputNombre = document.getElementById("input-nombre");
const inputPrecio = document.getElementById("input-precio");
const inputDescripcion = document.getElementById("input-descripcion");
const btnAgregar = document.getElementById("btn-agregar");

// --- Utilidades ---
function escapeHTML(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatearPrecio(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n.toFixed(2) : "0.00";
}

// --- Plantillas ---
function plantillaProducto(p, idx) {
  if (idx === editIndex) {
    // Vista de edición
    return `
      <li data-index="${idx}">
        <div>
          <label>
            Nombre:
            <input type="text" id="edit-nombre" value="${escapeHTML(p.nombre)}" />
          </label><br/><br/>
          <label>
            Precio:
            <input type="number" id="edit-precio" value="${escapeHTML(p.precio)}" step="0.01" />
          </label><br/><br/>
          <label>
            Descripción:
            <input type="text" id="edit-descripcion" value="${escapeHTML(p.descripcion)}" />
          </label><br/><br/>
          <button class="btn-guardar">Guardar</button>
          <button class="btn-cancelar">Cancelar</button>
        </div>
      </li>
    `;
  }

  // Vista normal
  return `
    <li data-index="${idx}">
      <strong>${escapeHTML(p.nombre)}</strong><br />
      Precio: $${formatearPrecio(p.precio)}<br />
      <em>${escapeHTML(p.descripcion)}</em><br/><br/>
      <button class="btn-editar">Editar</button>
      <button class="btn-eliminar">Eliminar</button>
    </li>
  `;
}

// --- Render ---
function renderizarLista() {
  const html = productos.map(plantillaProducto).join("");
  ulLista.innerHTML = html;
}

// --- Acciones ---
function agregarProducto() {
  const nombre = (inputNombre.value || "").trim();
  const precio = Number(inputPrecio.value);
  const descripcion = (inputDescripcion.value || "").trim();

  if (!nombre) {
    alert("Por favor, ingresa un nombre.");
    return;
  }
  if (!Number.isFinite(precio)) {
    alert("Por favor, ingresa un precio válido (número).");
    return;
  }
  if (!descripcion) {
    alert("Por favor, ingresa una descripción.");
    return;
  }

  productos.push({ nombre, precio, descripcion });
  guardarProductos();
  renderizarLista();

  inputNombre.value = "";
  inputPrecio.value = "";
  inputDescripcion.value = "";
  inputNombre.focus();
}

function iniciarEdicion(index) {
  editIndex = index;
  renderizarLista();
  // Enfocar el primer input de edición
  const input = document.getElementById("edit-nombre");
  if (input) input.focus();
}

function cancelarEdicion() {
  editIndex = null;
  renderizarLista();
}

function guardarEdicion(index) {
  const li = ulLista.querySelector(`li[data-index="${index}"]`);
  if (!li) return;

  const nombre = (li.querySelector("#edit-nombre")?.value || "").trim();
  const precio = Number(li.querySelector("#edit-precio")?.value);
  const descripcion = (li.querySelector("#edit-descripcion")?.value || "").trim();

  if (!nombre) {
    alert("El nombre no puede estar vacío.");
    return;
  }
  if (!Number.isFinite(precio)) {
    alert("Precio inválido.");
    return;
  }
  if (!descripcion) {
    alert("La descripción no puede estar vacía.");
    return;
  }

  productos[index] = { nombre, precio, descripcion };
  guardarProductos();
  editIndex = null;
  renderizarLista();
}

function eliminarProducto(index) {
  if (!confirm("¿Eliminar este producto?")) return;
  productos.splice(index, 1);
  guardarProductos();
  renderizarLista();
}

// --- Eventos ---
document.addEventListener("DOMContentLoaded", () => {
  renderizarLista();

  btnAgregar.addEventListener("click", agregarProducto);

  // Delegación de eventos para los botones dentro de la lista
  ulLista.addEventListener("click", (e) => {
    const target = e.target;
    if (!(target instanceof Element)) return;

    const li = target.closest("li[data-index]");
    if (!li) return;

    const index = Number(li.getAttribute("data-index"));

    if (target.classList.contains("btn-editar")) {
      iniciarEdicion(index);
    } else if (target.classList.contains("btn-cancelar")) {
      cancelarEdicion();
    } else if (target.classList.contains("btn-guardar")) {
      guardarEdicion(index);
    } else if (target.classList.contains("btn-eliminar")) {
      eliminarProducto(index);
    }
  });
});
