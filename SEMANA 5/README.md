
# Galería Interactiva — Semana 5

Proyecto de una **galería de imágenes** donde el usuario puede **agregar URLs**, **seleccionar** elementos, **eliminarlos** y **navegar** con atajos de teclado. Implementado con **HTML + CSS + JavaScript (DOM)**.

> Autor: Byron · Curso Semana 5

---

## 🗂 Estructura del proyecto

```
.
├── index.html   # Estructura del documento (secciones, controles, galería)
├── style.css    # Estilos visuales, layout, animaciones y clases utilitarias
└── script.js    # Lógica de interacción (agregar, seleccionar, eliminar, atajos)
```

---

## 🚀 Cómo ejecutar

1. Asegúrate de enlazar el JavaScript en `index.html`:
   ```html
   <script src="script.js" defer></script>
   ```
2. Abre el proyecto con un **servidor local** (recomendado para evitar políticas de seguridad `file://`).
   - Por ejemplo, con **VS Code**: extensión *Live Server* → *Open with Live Server*.
   - O cualquier servidor simple (`python -m http.server`, etc.).
3. Navega a la página y pega una **URL directa** de imagen (ej. termina en `.jpg`, `.png`, `.webp`) en el campo de texto.
4. Presiona **Agregar Imagen** o **Enter**.

> **Nota:** Algunas URLs que no apuntan directamente a un archivo de imagen (sino a una página HTML) **no cargarán**.

---

## ✨ Funcionalidades

- **Agregar imagen por URL**: habilita el botón cuando la URL es válida.
- **Validación visual**: el input muestra estado `invalid` si la URL no es válida.
- **Selección única**: clic o foco sobre un ítem marca la selección.
- **Eliminar imagen**: quita el elemento con transición suave.
- **Atajos de teclado**:
  - `Enter`: agrega imagen si el foco está en el input.
  - `Delete` / `Backspace`: elimina la imagen seleccionada.
  - `Esc`: deselecciona.
  - `←` `→` `↑` `↓`: navega entre imágenes.
- **Estado vacío**: muestra/oculta el mensaje "No hay imágenes" según contenido.
- **Año dinámico** en el footer.
- **Carga diferida** (`loading="lazy"`) para optimizar rendimiento.

---

## 🧩 Detalles de implementación

### HTML (`index.html`)
- Controles: `input[type="url"]`, botones **Agregar** y **Eliminar** (inicialmente deshabilitados).
- Mensaje de ayuda con atajos.
- Contenedor principal `#gallery` para las imágenes.
- Footer con `<span id="year">` para el año actual.

### CSS (`style.css`)
- Paleta oscura con variables CSS.
- Layout de galería con **CSS Grid** (`grid-template-columns: repeat(auto-fill, minmax(180px, 1fr))`).
- Tarjetas `.item` con `border-radius`, `box-shadow` y **animaciones**:
  - `@keyframes fadeInScale` aplicado mediante clase `.enter`.
  - Clase `.removed` para el desvanecimiento al eliminar.
- Estados y utilidades:
  - `.selected`: resalta el ítem activo con `outline` y `box-shadow`.
  - `.invalid`: marca el input con borde y `outline` ámbar.
  - `.sr-only`: ocultación accesible para lectores de pantalla.

### JavaScript (`script.js`)
- **Referencias** al DOM: `imgUrl`, `btnAdd`, `btnRemove`, `gallery`, `emptyMsg`, `year`.
- **Utilidades**:
  - `isValidUrl(str)`: valida sintaxis de URL (no garantiza que sea imagen).
  - `updateEmptyState()`: controla visibilidad del mensaje y el botón eliminar.
- **Creación de ítems**:
  - `createItem(src)`: genera un `figure.item` con `img` y `loading="lazy"`.
- **Agregar imagen**:
  - `addImage()`: valida, crea, inserta y limpia estado/animación.
- **Selección**:
  - `selectItem(el)`, `clearSelection()`: gestionan la selección única y UI.
- **Eliminar**:
  - `removeSelected()`: transiciona con `.removed` y, al finalizar, elimina el nodo.
- **Eventos**:
  - `input`: habilita/deshabilita el botón y marca `invalid`.
  - `click` en galería: delegación para seleccionar.
  - `keydown`: atajos (`Enter`, `Delete/Backspace`, `Esc`, flechas de navegación).
- **Precarga opcional**: `DEFAULT_IMAGES` con 3 URLs de Unsplash para pruebas.

---

## 🛠 Requisitos y compatibilidad

- Navegador moderno con soporte para **ES6** y `classList`, `closest`, `scrollIntoView`.
- Se recomienda servir por **HTTP/HTTPS** (no `file://`) para evitar bloqueos de contenido.

---

## ⚠️ Posibles problemas y soluciones

- **No carga la imagen**: asegúrate de que la URL apunte a un archivo con `Content-Type: image/*`. Prueba con `.jpg`, `.png`, `.webp` o enlaces de CDN.
- **Botón Agregar deshabilitado**: el input requiere una URL válida. Si quieres limitar a imágenes, agrega una heurística adicional (por extensión) o una verificación de `Content-Type`.
- **Mixed Content / CORS**: si sirves por `http` y cargas `https` (o viceversa), el navegador puede bloquear recursos. Usa `https` y un servidor local.

---

## 🔒 Accesibilidad

- Etiqueta `label` con `.sr-only` para el campo URL.
- Navegación por teclado y enfoque visual en elementos seleccionados.
- Uso de `aria-label` en secciones (`Controles de la galería`, `Galería de imágenes`).

---

## 📦 Mejoras sugeridas (TODO)

- Validar que la URL **sea de imagen** (p.ej., heurística por extensión o `fetch` para verificar `Content-Type`).
- Manejo de **error** en `img.onload / img.onerror` para mostrar mensaje amigable.
- Previsualización modal al hacer clic en una imagen.
- Persistencia en `localStorage` para recordar la galería entre sesiones.
- Drag & drop para reordenar elementos.

---

## 🧪 Ejemplo de URLs válidas

```text
https://picsum.photos/seed/flower/800/600
https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png
https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1200
```

---

## 📜 Licencia

Uso educativo. Ajusta y reutiliza libremente en tus prácticas.

