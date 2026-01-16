

//  utilidades 
const $ = (sel, ctx=document) => ctx.querySelector(sel);

const form = $('#formRegistro');
const inputNombre = $('#nombre');
const inputEmail = $('#email');
const inputPassword = $('#password');
const inputConfirm = $('#confirmPassword');
const inputEdad = $('#edad');

const errorNombre = $('#error-nombre');
const errorEmail = $('#error-email');
const errorPassword = $('#error-password');
const errorConfirm = $('#error-confirm');
const errorEdad = $('#error-edad');

const btnEnviar = $('#btnEnviar');
const btnReiniciar = $('#btnReiniciar');
const formMsg = $('#formMsg');

//  reglas de validación 
function validarNombre(v){
  const val = v.trim();
  if (!val) return {ok:false, msg:'El nombre es obligatorio.'};
  if (val.length < 3) return {ok:false, msg:'Debe tener al menos 3 caracteres.'};
  if (val.length > 60) return {ok:false, msg:'Máximo 60 caracteres.'};
  return {ok:true, msg:'El nombre es correcto.'};
}

function validarEmail(v){
  const val = v.trim();
  if (!val) return {ok:false, msg:'El correo es obligatorio.'};

  const re = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  if (!re.test(val)) return {ok:false, msg:'Formato de correo no válido.'};
  return {ok:true, msg:'Correo válido y aceptado.'};
}

function validarPassword(v){
  const val = v;
  if (!val) return {ok:false, msg:'La contraseña es obligatoria.'};
  if (val.length < 8) return {ok:false, msg:'Mínimo 8 caracteres.'};
  if (!/\d/.test(val)) return {ok:false, msg:'Debe incluir al menos 1 número.'};
  // símbolo común: !@#$%^&*()_+[]{};:'",.<>/?\|`~-
  if (!/[!@#$%^&*()_\-+\[\]{};:'",.<>/?\\|`~]/.test(val))
    return {ok:false, msg:'Debe incluir al menos 1 carácter especial.'};
  return {ok:true, msg:'Contraseña válida.'};
}

function validarConfirmacion(confirm, original){
  if (!confirm) return {ok:false, msg:'Repite tu contraseña.'};
  if (confirm !== original) return {ok:false, msg:'Las contraseñas no coinciden.'};
  return {ok:true, msg:'Las contraseñas coinciden.'};
}

function validarEdad(v){
  const n = Number(v);
  if (!v) return {ok:false, msg:'La edad es obligatoria.'};
  if (!Number.isInteger(n) || n < 0) return {ok:false, msg:'Ingresa un número válido.'};
  if (n < 18) return {ok:false, msg:'Debes ser mayor o igual a 18 años.'};
  if (n > 120) return {ok:false, msg:'Verifica la edad ingresada.'};
  return {ok:true, msg:'La Edad es válida.'};
}

// pintado de estados 
function setEstado(input, msgEl, {ok, msg}){
  // mensaje
  msgEl.textContent = msg || '';
  msgEl.classList.remove('error','success');
  msgEl.classList.add(ok ? 'success' : 'error');

  // borde del input
  input.classList.remove('is-valid','is-invalid');
  input.classList.add(ok ? 'is-valid' : 'is-invalid');

  // accesibilidad
  input.setAttribute('aria-invalid', String(!ok));
}

function estadoPorDefecto(){
  // limpiar mensajes y bordes
  [ [inputNombre,errorNombre],
    [inputEmail,errorEmail],
    [inputPassword,errorPassword],
    [inputConfirm,errorConfirm],
    [inputEdad,errorEdad] ].forEach(([inp, msg])=>{
      msg.textContent = '';
      msg.classList.remove('error','success');
      inp.classList.remove('is-valid','is-invalid');
      inp.removeAttribute('aria-invalid');
  });
  formMsg.className = 'form-msg';
  formMsg.textContent = '';
  btnEnviar.disabled = true;
}

//  validaciones en tiempo real 
function validarCampoNombre(){
  const res = validarNombre(inputNombre.value);
  setEstado(inputNombre, errorNombre, res);
  actualizarBoton();
}
function validarCampoEmail(){
  const res = validarEmail(inputEmail.value);
  setEstado(inputEmail, errorEmail, res);
  actualizarBoton();
}
function validarCampoPassword(){
  const res = validarPassword(inputPassword.value);
  setEstado(inputPassword, errorPassword, res);
  // revalida confirmación si ya hay algo escrito
  if (inputConfirm.value) validarCampoConfirm();
  actualizarBoton();
}
function validarCampoConfirm(){
  const res = validarConfirmacion(inputConfirm.value, inputPassword.value);
  setEstado(inputConfirm, errorConfirm, res);
  actualizarBoton();
}
function validarCampoEdad(){
  const res = validarEdad(inputEdad.value);
  setEstado(inputEdad, errorEdad, res);
  actualizarBoton();
}

//  habilitar/deshabilitar envío 
function formularioValido(){
  return (
    validarNombre(inputNombre.value).ok &&
    validarEmail(inputEmail.value).ok &&
    validarPassword(inputPassword.value).ok &&
    validarConfirmacion(inputConfirm.value, inputPassword.value).ok &&
    validarEdad(inputEdad.value).ok
  );
}

function actualizarBoton(){
  btnEnviar.disabled = !formularioValido();
}

//  eventos 
['input','blur'].forEach(evt=>{
  inputNombre.addEventListener(evt, validarCampoNombre);
  inputEmail.addEventListener(evt, validarCampoEmail);
  inputPassword.addEventListener(evt, validarCampoPassword);
  inputConfirm.addEventListener(evt, validarCampoConfirm);
  inputEdad.addEventListener(evt, validarCampoEdad);
});

// Envío (no recarga, muestra confirmación)
form.addEventListener('submit', (e)=>{
  e.preventDefault();
  if (!formularioValido()){
    formMsg.className = 'form-msg error';
    formMsg.textContent = 'Revise los campos que se encuentran marcados en rojo.';
    return;
  }
  formMsg.className = 'form-msg ok';
  formMsg.textContent = '✅ ¡El Formulario fue enviado de manera correcta!';
  alert('✅ La validación es correcta. ¡ El Formulario está listo para enviar!');
});

// Reinicio
btnReiniciar.addEventListener('click', ()=>{
  // El evento reset limpia los valores; nosotros limpiamos estados visuales
  setTimeout(estadoPorDefecto, 0);
});

// Estado inicial
estadoPorDefecto();
