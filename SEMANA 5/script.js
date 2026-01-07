
// Referencias
const urlInput = document.getElementById('imgUrl');
const btnAdd   = document.getElementById('btnAdd');
const btnRemove= document.getElementById('btnRemove');
const gallery  = document.getElementById('gallery');
const emptyMsg = document.getElementById('emptyMsg');
const yearEl   = document.getElementById('year');

// Año dinámico
yearEl.textContent = new Date().getFullYear();

// Utilidades
function isValidUrl(str){ try { new URL(str); return true; } catch { return false; } }
function updateEmptyState(){
  const hasItems = gallery.querySelector('.item') !== null;
  emptyMsg.style.display = hasItems ? 'none' : 'block';
  btnRemove.disabled = !hasItems || !gallery.querySelector('.selected');
}

// Crear item

function createItem(src) {
  const figure = document.createElement('figure');
  figure.className = 'item enter';

  const img = document.createElement('img');
  img.src = src;
  img.alt = 'Imagen añadida por el usuario';
  img.loading = 'lazy';

  // Si la imagen falla, quitamos el item y avisamos
  img.addEventListener('error', () => {
    figure.remove();
    updateEmptyState();
    alert('No se pudo cargar la imagen. Asegúrate de que la URL apunte a un archivo de imagen.');
  });

  figure.appendChild(img);
  return figure;
}



// Agregar
function addImage(){
  const src = urlInput.value.trim();
  if(!isValidUrl(src)){ urlInput.classList.add('invalid'); return; }
  const item = createItem(src);
  gallery.appendChild(item);
  setTimeout(() => item.classList.remove('enter'), 0); // limpia animación
  urlInput.value = ''; urlInput.classList.remove('invalid'); btnAdd.disabled = true;
  clearSelection(); updateEmptyState();
}

// Selección única
function selectItem(el){
  if(!el) return;
  const prev = gallery.querySelector('.selected');
  if(prev) prev.classList.remove('selected');
  el.classList.add('selected');
  btnRemove.disabled = false;
}
function clearSelection(){
  const prev = gallery.querySelector('.selected');
  if(prev) prev.classList.remove('selected');
  btnRemove.disabled = true;
}

// Eliminar (fade-out)
function removeSelected(){
  const sel = gallery.querySelector('.selected');
  if(!sel) return;
  sel.classList.add('removed');
  sel.addEventListener('transitionend', () => {
    sel.remove(); updateEmptyState();
  }, { once: true });
}

// Eventos
urlInput.addEventListener('input', () => {
  const valid = isValidUrl(urlInput.value.trim());
  urlInput.classList.toggle('invalid', !valid && urlInput.value.trim() !== '');
  btnAdd.disabled = !valid;
});
btnAdd.addEventListener('click', addImage);
btnRemove.addEventListener('click', removeSelected);

// Delegación para seleccionar
gallery.addEventListener('click', (ev) => {
  const item = ev.target.closest('.item');
  if(!item) return;
  selectItem(item);
});

// Atajos de teclado
document.addEventListener('keydown', (ev) => {
  const items = Array.from(gallery.querySelectorAll('.item'));
  const selected = gallery.querySelector('.selected');

  switch(ev.key){
    case 'Enter':
      if(document.activeElement === urlInput && !btnAdd.disabled){ addImage(); }
      break;
    case 'Delete':
    case 'Backspace':
      removeSelected(); break;
    case 'Escape':
      clearSelection(); break;
    case 'ArrowRight':
    case 'ArrowDown':
    case 'ArrowLeft':
    case 'ArrowUp':
      if(items.length === 0) return;
      let idx = selected ? items.indexOf(selected) : -1;
      if(idx === -1){ selectItem(items[0]); items[0].scrollIntoView({ block: 'nearest', inline: 'nearest' }); return; }
      if(ev.key === 'ArrowRight' || ev.key === 'ArrowDown') idx = (idx + 1) % items.length;
      if(ev.key === 'ArrowLeft'  || ev.key === 'ArrowUp')   idx = (idx - 1 + items.length) % items.length;
      selectItem(items[idx]);
      items[idx].scrollIntoView({ block: 'nearest', inline: 'nearest' });
      break;
  }
});

// Precarga opcional (puedes borrar este bloque)
const DEFAULT_IMAGES = [
  'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200',
  'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1200',
  'https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1200'
];
DEFAULT_IMAGES.forEach(src => {
  const item = createItem(src);
  gallery.appendChild(item);
  setTimeout(() => item.classList.remove('enter'), 0);
});
updateEmptyState();
