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
  const inputhidden = document.getElementById("dias-" + plan);
  if (inputhidden) {
    inputhidden.value = dias;
  }
  const inputprecio = document.getElementById("precio-hidden-" + plan);
  if (inputprecio) {
    inputprecio.value = precio.toFixed(2);
  }
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
  const selectdeportes = document.querySelectorAll("select[id^='deporte-']");
  const imagen = document.getElementById("imagen-deporte");

  if (imagen) {
    const imagenes = {
      "futbol sala": "static/images/sport.png",
      boxeo: "static/images/boxeo.png",
      rugby: "static/images/rugby.png",
    };

    selectdeportes.forEach((select) => {
      if (select) {
        select.addEventListener("change", (e) => {
          const deporte = e.target.value;
          if (imagen && imagenes[deporte]) {
            imagen.src = imagenes[deporte];
          }
        });
      }
    });
  }
  // Manejo de formularios de planes
  const formularios = document.querySelectorAll("form[id^='form-']");
  formularios.forEach((form) => {
    form.addEventListener("submit", (e) => {
      console.log("Formulario enviado!");
      const planid = form.id.replace("form-", "");
      const selectvisible = document.getElementById("deporte-" + planid);
      const selectoculto = document.getElementById(
        "select-dentro-form-" + planid
      );

      if (selectvisible && selectoculto) {
        selectoculto.value = selectvisible.value;
      }

      const boton = form.querySelector(".boton-comprar");
      if (boton) {
        boton.textContent = "Agregando...";
        boton.disabled = true;

        // Restaurar el botón después de un tiempo (por si hay error)
        setTimeout(() => {
          boton.textContent = "comprar";
          boton.disabled = false;
        }, 3000);
      }
    });
  });
  //------------------------------------------------------------------------------------Mobile Navbar
  const burger = document.getElementById("burger-button");
  const mobileMenu = document.getElementById("mobile-menu");
  const miPerfil = document.getElementById("mobile-menu-item-miperfil");
  const cerrarSesion = document.getElementById("mobile-menu-item-cerrarsesion");

  function mostrarMenu() {
    mobileMenu.classList.remove("opacity-0", "scale-95", "pointer-events-none");
    mobileMenu.classList.add("opacity-100", "scale-100");
  }
  function ocultarMenu() {
    mobileMenu.classList.remove("opacity-100", "scale-100");
    mobileMenu.classList.add("opacity-0", "scale-95", "pointer-events-none");
  }
  if (burger) {
    burger.addEventListener("click", (e) => {
      e.stopPropagation();
      if (mobileMenu.classList.contains("opacity-0")) {
        mostrarMenu();
      } else {
        ocultarMenu();
      }
    });
  }

  // Cierra el menú si se hace clic fuera
  if (mobileMenu) {
    document.addEventListener("click", (e) => {
      if (!mobileMenu.contains(e.target) && !burger.contains(e.target)) {
        ocultarMenu();
      }
    });
  }

  // Cierra el menú al hacer clic en los ítems
  if (miPerfil) {
    miPerfil.addEventListener("click", ocultarMenu);
  }
  if (cerrarSesion) {
    cerrarSesion.addEventListener("click", ocultarMenu);
  }

  //------------------------------------------------------------------------------------Funcionalidad toast: cerrar al click en la X
  const botonCerrar = document.getElementById("button_alert");

  if (botonCerrar) {
    botonCerrar.onclick = (e) => {
      e.preventDefault();
      const alert = document.getElementById("toast-alert");
      if (alert) alert.classList.add("hidden");
    };
  }

  // Ocultar toast después de 8 segundos
  setTimeout(() => {
    const alertBox = document.getElementById("toast-alert");
    if (alertBox) {
      alertBox.classList.add("hidden");
    }
  }, 3000);

  //------------------------------------------------------------------------------------Funcion para que aparezca la barra amarilla debajo del logo de la ruta actual
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

  //------------------------------------------------------------------------------------Funcionalidad del Menu
  const avatar = document.getElementById("menu-user-avatar");
  const menu = document.getElementById("menu-ul");
  const miPerfil2 = document.getElementById("menu-item-miperfil");
  const cerrarSesion2 = document.getElementById("menu-item-cerrarsesion");

  function mostrarMenu2() {
    menu.classList.remove("opacity-0", "scale-95", "pointer-events-none");
    menu.classList.add("opacity-100", "scale-100");
  }
  function ocultarMenu2() {
    menu.classList.remove("opacity-100", "scale-100");
    menu.classList.add("opacity-0", "scale-95", "pointer-events-none");
  }
  if (avatar) {
    avatar.addEventListener("click", (e) => {
      e.stopPropagation();
      if (menu.classList.contains("opacity-0")) {
        mostrarMenu2();
      } else {
        ocultarMenu2();
      }
    });
  }

  // Cierra el menú si se hace clic fuera
  if (menu) {
    document.addEventListener("click", (e) => {
      if (!menu.contains(e.target) && !avatar.contains(e.target)) {
        ocultarMenu2();
      }
    });
  }

  // Cierra el menú al hacer clic en los ítems
  if (miPerfil2) {
    miPerfil2.addEventListener("click", ocultarMenu2);
  }
  if (cerrarSesion2) {
    cerrarSesion2.addEventListener("click", ocultarMenu2);
  }

  //------------------------------------------------------------------------------------UserInputs
  const button = document.getElementById("editar_perfil");
  const button_guardar = document.getElementById("guardar_perfil");
  const button_cancelar = document.getElementById("cancelar_perfil");

  const inputs = [
    document.getElementById("user_nombre"),
    document.getElementById("user_apellido"),
    document.getElementById("user_usuario"),
    document.getElementById("user_telefono"),
    document.getElementById("user_nacimiento"),
  ].filter((input) => input !== null); 

  const valoresOriginales = {};

  // Guardamos los valores originales una vez y preparamos los listeners de los inputs
  if (inputs.length > 0) {
    inputs.forEach((input) => {
      valoresOriginales[input.name] = input.value;

      const label = input.parentElement.querySelector(
        `label[for="${input.id}"]`
      );

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
  }

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

  if (button) {
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
  }
  if (button_cancelar) {
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
  }


  //----------------- Script para el efecto 3D sutil que sigue al cursor
    const cards = document.querySelectorAll('.efecto-3d');
    cards.forEach(card => {

      let currentRotationX = 0;
      let currentRotationY = 0;
      let targetRotationX = 0;
      let targetRotationY = 0;

      function handleMouseMove(event) {
          const rect = card.getBoundingClientRect();
          
          const centerX = rect.left + rect.width / 2;
          const centerY = rect.top + rect.height / 2;
          
          const mouseX = event.clientX;
          const mouseY = event.clientY;
          
          const deltaX = mouseX - centerX;
          const deltaY = mouseY - centerY;
          
          targetRotationY = (deltaX / rect.width) * 8;  
          targetRotationX = -(deltaY / rect.height) * 8; 
      }

      function animate() {
          currentRotationX += (targetRotationX - currentRotationX) * 0.5;
          currentRotationY += (targetRotationY - currentRotationY) * 0.5;
          
          card.style.transform = `perspective(1000px) rotateX(${currentRotationX}deg) rotateY(${currentRotationY}deg)`;
          
          requestAnimationFrame(animate);
      }

      function handleMouseLeave() {
          targetRotationX = 0;
          targetRotationY = 0;
      }

      card.addEventListener('mousemove', handleMouseMove);
      card.addEventListener('mouseleave', handleMouseLeave);

      animate();
  });
  
});


  let currentIndex = 0;
  const images = document.querySelectorAll("#carrusel img");
  const totalImages = images.length;

  function updateCarousel() {
    const container = document.getElementById("carrusel");
    if (!container) return;
    container.style.transform = `translateX(-${currentIndex * 100}%)`;
  }

  function nextSlide() {
    currentIndex = (currentIndex + 1) % totalImages;
    updateCarousel();
  }

  function prevSlide() {
    currentIndex = (currentIndex - 1 + totalImages) % totalImages;
    updateCarousel();
  }
  setInterval(nextSlide, 3000);

  const titulo = document.getElementById("titulo-animado");
  if (titulo) {
    const texto = titulo.innerText;
    const letras = texto.split("").map((char) => {
      if (char === " ") return `<span class="inline-block">&nbsp;</span>`;
      if (char === "*") return "<br>";
      return `<span class="inline-block transition hover:-translate-y-[0.2vw]">${char}</span>`;
    });
    titulo.innerHTML = letras.join("");
  }



// -------------------- RESERVAS ----------------------
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

const reserveButton = document.getElementById("button-reserva");
if (reserveButton) {
  reserveButton.addEventListener('click', async function (e) {
    e.preventDefault();

    const selectedDays = [];
    dayCheckboxes.forEach(checkbox => {
      if (checkbox.checked) {
        selectedDays.push(checkbox.value);
      }
    });

    if (selectedDays.length === 0) {
      alert('Por favor selecciona al menos un día para tu reserva.');
      return;
    }

    // Obtener otros valores del formulario
    const trainingType = document.querySelector('#type-exercise').value;
    const trainingType_number = parseInt(trainingType.value); // Convertir a número el tipo de entrenamiento
    const startTime = document.querySelectorAll('input[type="time"]')[0].value;
    const endTime = document.querySelectorAll('input[type="time"]')[1].value;
    const comments = document.querySelector('#comment-area').value;

    // Validar que se seleccionó un tipo de entrenamiento válido
    if (isNaN(trainingType) || trainingType <= 0) {
      alert('Por favor selecciona un tipo de entrenamiento válido.');
      return;
    }

    // Preparar datos para enviar
    const datos_reserva = {
      dias: selectedDays, 
      tipo_entrenamiento: trainingType,
      hora_inicio: startTime,
      hora_fin: endTime,
      comentarios: comments
    };

    console.log('Datos de reserva:', datos_reserva);

    try {
      // Enviar datos al servidor Flask
      const response = await fetch('/procesar_reserva', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(datos_reserva)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        alert("¡Reserva exitosa!");
        // limpiar el formulario después de una reserva exitosa
        limpiarFormulario();
      } else {
        alert(`Error: ${result.error || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error("Error al procesar la reserva:", error);
      alert("Error de conexión. Por favor, intenta nuevamente.");
    }
  });
}

// Función auxiliar para limpiar el formulario después de una reserva exitosa
function limpiarFormulario() {
  // Desmarcar todos los checkboxes de días
  dayCheckboxes.forEach(checkbox => {
    checkbox.checked = false;
    const label = checkbox.nextElementSibling;
    label.classList.remove('bg-yellow-400', 'text-gray-800', 'font-semibold');
    label.classList.add('bg-white', 'text-gray-700');
  });

  // Resetear select de tipo de entrenamiento
  const typeExercise = document.querySelector('#type-exercise');
  if (typeExercise) typeExercise.selectedIndex = 0;

  // Resetear horarios a valores por defecto
  const timeInputs = document.querySelectorAll('input[type="time"]');
  if (timeInputs[0]) timeInputs[0].value = '09:00';
  if (timeInputs[1]) timeInputs[1].value = '10:00';

  // Limpiar comentarios
  const commentArea = document.querySelector('#comment-area');
  if (commentArea) commentArea.value = '';
}

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