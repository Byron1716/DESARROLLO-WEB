// ====== Interactividad con JavaScript ======

document.addEventListener('DOMContentLoaded', () => {
  // Botón para mostrar alerta personalizada (Bootstrap Alert)
  const btnAlerta = document.getElementById('btnAlerta');
  const alertContainer = document.getElementById('alertContainer');

  btnAlerta.addEventListener('click', () => {
    // Limpiar alertas anteriores
    alertContainer.innerHTML = '';

    const alert = document.createElement('div');
    alert.className = 'alert alert-info alert-dismissible fade show';
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
      <strong>¡Hola,!</strong> Esta alerta es para que no lo pienses mas y te dejes llevar por la brisa el mar y la arena.
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
    `;
    alertContainer.appendChild(alert);

    // Desaparecer automáticamente después de 6s 
    setTimeout(() => {
      const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
      alertInstance.close();
    }, 8000);
  });

  // ===== Validación del formulario =====
  const form = document.getElementById('formContacto');
  const nombre = document.getElementById('nombre');
  const email = document.getElementById('email');
  const mensaje = document.getElementById('mensaje');

  // Validaciones simples
  const esEmailValido = (valor) => {
    // Expresión regular básica para emails
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
    return regex.test(valor);
  };

  const marcarValido = (input, valido) => {
    input.classList.remove('is-valid', 'is-invalid');
    input.classList.add(valido ? 'is-valid' : 'is-invalid');
  };

  // Validación en tiempo real
  nombre.addEventListener('input', () => marcarValido(nombre, nombre.value.trim().length > 0));
  email.addEventListener('input', () => marcarValido(email, esEmailValido(email.value.trim())));
  mensaje.addEventListener('input', () => marcarValido(mensaje, mensaje.value.trim().length >= 10));

  form.addEventListener('submit', (e) => {
    e.preventDefault(); // Evita el envío mientras validamos

    const vNombre = nombre.value.trim().length > 0;
    const vEmail = esEmailValido(email.value.trim());
    const vMensaje = mensaje.value.trim().length >= 10;

    marcarValido(nombre, vNombre);
    marcarValido(email, vEmail);
    marcarValido(mensaje, vMensaje);

    const esValido = vNombre && vEmail && vMensaje;

    if (esValido) {
      // Mostrar alerta de éxito y resetear
      alertContainer.innerHTML = '';
      const ok = document.createElement('div');
      ok.className = 'alert alert-success alert-dismissible fade show';
      ok.setAttribute('role', 'alert');
      ok.innerHTML = `
        ✅ ¡Gracias por escribirnos! Responderemos pronto.
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
      `;
      alertContainer.appendChild(ok);

      form.reset();
      [nombre, email, mensaje].forEach(i => i.classList.remove('is-valid', 'is-invalid'));
    } else {
      // Desplazar a la primera invalidación
      const firstInvalid = [nombre, email, mensaje].find(i => i.classList.contains('is-invalid'));
      if (firstInvalid) firstInvalid.focus();
    }
  });
});
