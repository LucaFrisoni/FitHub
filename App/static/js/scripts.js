// funcion que actualiza el precio segun los dias seleccionados
function updateprice(plan, dias) {
  const plandiv = document.getElementById(plan);
  const precio3 = parseInt(plandiv.dataset.precio3);
  const precio5 = parseInt(plandiv.dataset.precio5);
  dias = parseInt(dias);
  let precio;
  if (dias == 5) {
    precio = precio5;
  } else {
    precio = precio3;
  }
  const nuevoprecio = document.getElementById("precio-" + plan);
  nuevoprecio.textContent = "$" + precio;
  plandiv.dataset.diaselegidos = dias;
}

document.addEventListener("DOMContentLoaded", () => {
  // Código del primer bloque...
  // ------------------------------------------updateprice y botones .button-dias
  const botonesdias = document.querySelectorAll(".button-dias");
  botonesdias.forEach((boton) => {
    boton.addEventListener("click", () => {
      const plan = boton.closest(".plan").id;
      const dias = parseInt(boton.dataset.dias);
      updateprice(plan, dias);
      const botonesplan = boton
        .closest(".dias-buttons")
        .querySelectorAll(".button-dias");
      botonesplan.forEach((b) => {
        b.classList.remove("activo", "bg-primary", "text-black", "opacity-100");
        b.classList.add("inactivo", "bg-gray-600", "text-white", "opacity-70");
      });
      boton.classList.remove(
        "inactivo",
        "bg-gray-600",
        "text-white",
        "opacity-70"
      );
      boton.classList.add("activo", "bg-primary", "text-black", "opacity-100");
    });
  });

  //------------------------------------------ Cambio de imagen según el deporte
  const selectdeporte = document.querySelector("select[id^='deporte-']");
  const imagen = document.getElementById("imagen-deporte");
  if (selectdeporte && imagen) {
    const imagenes = {
      "futbol sala": "static/images/sport.png",
      boxeo: "static/images/boxeo.png",
      rugby: "static/images/rugby.png",
    };
    selectdeporte.addEventListener("change", (e) => {
      const deporte = e.target.value;
      imagen.src = imagenes[deporte];
    });
  }

  //------------------------------------------ Funcionalidad toast: cerrar al click en la X
  const botonCerrar = document.getElementById("button_alert_login");
  if (botonCerrar) {
    botonCerrar.onclick = () => {
      const alertLogin = document.getElementById("alert-login");
      if (alertLogin) alertLogin.classList.add("hidden");
    };
  }

  // Ocultar toast después de 8 segundos
  setTimeout(() => {
    const alertBox = document.getElementById("alert-login");
    if (alertBox) {
      alertBox.classList.add("hidden");
    }
  }, 3000);

  //------------------------------------------ Funcion para que aparezca la barra amarilla debajo del logo de la ruta actual
  const links = document.querySelectorAll(".nav-link");
  const actualruta = window.location.pathname;
  let linkactivo = null;
  links.forEach((link) => {
    // para que quede la barra debajo del logo de la ruta actual
    const linkbarra = new URL(link.href).pathname;
    if (linkbarra == actualruta) {
      linkactivo = link;
      link.classList.add("active");
    }
    // para cuando el mouse pasa por encima de un logo que cambie a ese
    link.addEventListener("mouseenter", () => {
      links.forEach((link) => link.classList.remove("active"));
      link.classList.add("active");
    });
    //  para cuando el mouse sale de un logo que vuelva al de la ruta actual
    link.addEventListener("mouseleave", () => {
      links.forEach((link) => link.classList.remove("active"));
      if (linkactivo) {
        linkactivo.classList.add("active");
      }
    });
  });

  //------------------------------------------ Funcionalidad del Menu
  const avatar = document.getElementById("menu-user-avatar");
  const menu = document.getElementById("menu-ul");
  const miPerfil = document.getElementById("menu-item-miperfil");
  const cerrarSesion = document.getElementById("menu-item-cerrarsesion");

  function mostrarMenu() {
    menu.classList.remove("opacity-0", "scale-95", "pointer-events-none");
    menu.classList.add("opacity-100", "scale-100");
  }
  function ocultarMenu() {
    menu.classList.remove("opacity-100", "scale-100");
    menu.classList.add("opacity-0", "scale-95", "pointer-events-none");
  }

  avatar.addEventListener("click", (e) => {
    e.stopPropagation();
    if (menu.classList.contains("opacity-0")) {
      mostrarMenu();
    } else {
      ocultarMenu();
    }
  });

  // Cierra el menú si se hace clic fuera
  document.addEventListener("click", (e) => {
    if (!menu.contains(e.target) && !avatar.contains(e.target)) {
      ocultarMenu();
    }
  });

  // Cierra el menú al hacer clic en los ítems
  miPerfil.addEventListener("click", ocultarMenu);
  cerrarSesion.addEventListener("click", ocultarMenu);

  //------------------------------------------ UserInputs
  const button = document.getElementById("editar_perfil");
  const button_guardar = document.getElementById("guardar_perfil");
  const button_cancelar = document.getElementById("cancelar_perfil");

  const inputs = [
    document.getElementById("user_nombre"),
    document.getElementById("user_apellido"),
    document.getElementById("user_usuario"),
    document.getElementById("user_telefono"),
    document.getElementById("user_nacimiento"),
  ];

  const valoresOriginales = {};

  // Guardamos los valores originales una vez y preparamos los listeners de los inputs
  inputs.forEach((input) => {
    valoresOriginales[input.name] = input.value;

    const label = input.parentElement.querySelector(`label[for="${input.id}"]`);

    input.addEventListener("input", () => {
      if (label) {
        if (
          input.value !== valoresOriginales[input.name] &&
          input.value !== ""
        ) {
          label.classList.add("opacity-0", "scale-95");
        } else {
          label.classList.remove("opacity-0", "scale-95");
        }
      }
    });
  });

  function mostrarBotones() {
    button.classList.remove("opacity-100", "scale-100");
    button.classList.add("opacity-0", "scale-95", "pointer-events-none");

    button_guardar.classList.remove(
      "opacity-0",
      "scale-95",
      "pointer-events-none"
    );
    button_cancelar.classList.remove(
      "opacity-0",
      "scale-95",
      "pointer-events-none"
    );
    button_guardar.classList.add("opacity-100", "scale-100");
    button_cancelar.classList.add("opacity-100", "scale-100");
  }
  function ocultarBtones() {
    button.classList.remove("opacity-0", "scale-95", "pointer-events-none");
    button.classList.add("opacity-100", "scale-100");
    button_guardar.classList.remove("opacity-100", "scale-100");
    button_cancelar.classList.remove("opacity-100", "scale-100");
    button_guardar.classList.add(
      "opacity-0",
      "scale-95",
      "pointer-events-none"
    );
    button_cancelar.classList.add(
      "opacity-0",
      "scale-95",
      "pointer-events-none"
    );
  }

  button.addEventListener("click", (e) => {
    e.preventDefault();
    mostrarBotones();

    // Habilitamos todos los inputs
    inputs.forEach((input) => {
      input.disabled = false;
    });

    // Hacemos foco en el primer campo
    inputs[0].focus();
  });

  button_cancelar.addEventListener("click", (e) => {
    e.preventDefault();
    ocultarBtones();

    // Restauramos valores originales y deshabilitamos inputs
    inputs.forEach((input) => {
      input.value = valoresOriginales[input.name];
      input.disabled = true;
      const label = input.parentElement.querySelector(
        `label[for="${input.id}"]`
      );
      if (label) {
        label.classList.remove("opacity-0", "scale-95");
      }
    });
  });
});

// Funcionalidad de los checkboxes de días
const dayCheckboxes = document.querySelectorAll('.day-checkbox');

dayCheckboxes.forEach(checkbox => {
  checkbox.addEventListener('change', function () {
    const label = this.nextElementSibling;
    if (this.checked) {
      label.classList.add('bg-yellow-400', 'text-gray-800', 'font-semibold');
      label.classList.remove('bg-white', 'text-gray-700');
    } else {
      label.classList.remove('bg-yellow-400', 'text-gray-800', 'font-semibold');
      label.classList.add('bg-white', 'text-gray-700');
    }
  });
});

// Funcionalidad del botón reservar
const reserveButtons = document.querySelectorAll('button');
reserveButtons.forEach(button => {
  if (button.textContent.trim() === 'RESERVAR') {
    button.addEventListener('click', function (e) {
      e.preventDefault();

      // Obtener días seleccionados
      const selectedDays = [];
      dayCheckboxes.forEach(checkbox => {
        if (checkbox.checked) {
          selectedDays.push(checkbox.value);
        }
      });

      // Obtener otros valores del formulario
      const trainingType = document.querySelector('select').value;
      const startTime = document.querySelectorAll('input[type="time"]')[0].value;
      const endTime = document.querySelectorAll('input[type="time"]')[1].value;
      const comments = document.querySelector('textarea').value;

      if (selectedDays.length === 0) {
        alert('Por favor selecciona al menos un día para tu reserva.');
        return;
      }

      // Mostrar confirmación
      const message = `¡Reserva realizada con éxito!
             
      Días: ${selectedDays.join(', ')}
      Entrenamiento: ${trainingType}
      Horario: ${startTime} - ${endTime}
      ${comments ? 'Comentarios: ' + comments : ''}`;

      alert(message);
    });
  }
});

// Mejorar la experiencia táctil en móviles
const touchElements = document.querySelectorAll('.day-button, button, select, input, textarea');
touchElements.forEach(element => {
  element.addEventListener('touchstart', function () {
    this.style.transform = 'scale(0.98)';
  });

  element.addEventListener('touchend', function () {
    this.style.transform = 'scale(1)';
  });
});