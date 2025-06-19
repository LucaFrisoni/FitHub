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
  //navbar principal ocultandose en el home hasta cierto punto
  const navbar = document.getElementById("navbar");

  if (window.location.pathname === "/") {
    navbar.classList.add("-translate-y-full");

    window.addEventListener("scroll", () => {
      if (window.scrollY > innerHeight * 0.2) {
        navbar.classList.remove("-translate-y-full");
        navbar.classList.add("translate-y-0");
      } else {
        navbar.classList.remove("translate-y-0");
        navbar.classList.add("-translate-y-full");
      }
    });
  }

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
  const cards = document.querySelectorAll(".efecto-3d");
  cards.forEach((card) => {
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

    card.addEventListener("mousemove", handleMouseMove);
    card.addEventListener("mouseleave", handleMouseLeave);

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

//Script para subir una imagen en planes
function abrirModalPlan() {
  document.getElementById("modal-imagen-plan").classList.add("flex");
  document.getElementById("modal-imagen-plan").classList.remove("hidden");
}

function cerrarModalPlan() {
  document.getElementById("modal-imagen-plan").classList.add("hidden");
  document.getElementById("modal-imagen-plan").classList.remove("flex");
}

function previewFotoPlan(input) {
  const preview = document.getElementById("preview-imagen-plan");
  const file = input.files[0];

  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
}

//otro script para subir imagenes pero al editar el plan
// Imagen actual del plan para restaurar al cerrar el modal
const previewOriginalPlan =
  "{% if plan.Imagen and plan.Imagen != 'default_plan.jpg' %}{{ url_for('static', filename='images/uploads/planes/' + plan.Imagen) }}{% else %}{{ url_for('static', filename='images/default_plan.jpg') }}{% endif %}";


const formSubirImagen = document.getElementById("form-subir-imagen-plan");
  if (formSubirImagen) {
    formSubirImagen.addEventListener("submit", function (e) {
      e.preventDefault();
      mostrarLoaderPlan();

    const formData = new FormData(this);

      fetch(this.action, {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          if (data.success) {
            const previewPrincipal = document.getElementById("preview-imagen-principal");
            if (previewPrincipal) {
              previewPrincipal.src = data.url;
            }

            const hiddenInput = document.getElementById("nombre_imagen_plan");
            if (hiddenInput) {
              hiddenInput.value = data.filename;
            }

            cerrarModalPlan();
            formChanged = true;

            console.log("Imagen subida correctamente");
          } else {
            alert("Error: " + (data.error || "Error desconocido"));
            ocultarLoaderPlan();
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("Error al subir la imagen: " + error.message);
          ocultarLoaderPlan();
        });
    });
  }

function mostrarLoaderPlan() {
  document.getElementById("loader").classList.add("flex");
  document.getElementById("loader").classList.remove("hidden");

  document.getElementById("btn-submit-plan").disabled = true;

  document.getElementById("format-plan").classList.remove("flex");
  document.getElementById("format-plan").classList.add("hidden");

  document.getElementById("imagen_plan_prev").classList.add("hidden");
}

function ocultarLoaderPlan() {
  document.getElementById("loader").classList.add("hidden");
  document.getElementById("loader").classList.remove("flex");

  document.getElementById("btn-submit-plan").disabled = false;

  document.getElementById("format-plan").classList.add("flex");
  document.getElementById("format-plan").classList.remove("hidden");

  document.getElementById("imagen_plan_prev").classList.remove("hidden");
}

function abrirModalPlan() {
  document.getElementById("modal-imagen-plan").classList.add("flex");
  document.getElementById("modal-imagen-plan").classList.remove("hidden");

  // Resetear el preview del modal a la imagen actual
  document.getElementById("preview-imagen-plan").src = previewOriginalPlan;
}

function previewFotoPlan(input) {
  const preview = document.getElementById("preview-imagen-plan");
  const file = input.files[0];

  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
}

function cerrarModalPlan() {
  document.getElementById("modal-imagen-plan").classList.add("hidden");
  document.getElementById("modal-imagen-plan").classList.remove("flex");

  // Restaurar vista previa a la imagen actual del plan
  document.getElementById("preview-imagen-plan").src = previewOriginalPlan;
  document.getElementById("form-subir-imagen-plan").reset();

    // Asegurar que el loader está oculto
    ocultarLoaderPlan();
  }
  // Validación en tiempo real
   const form = document.getElementById("form-editar");

  // Validación antes del envío
  form.addEventListener("submit", function (e) {
    let isValid = true;
    let errors = [];

    // Validar nombre
    const nombre = document.getElementById("nombre").value.trim();
    if (!nombre || nombre.length < 3) {
      errors.push("El nombre debe tener al menos 3 caracteres");
      isValid = false;
    }

    // Validar precio 3 días
    const precio3 = parseFloat(document.getElementById("precio_3_dias").value);
    if (isNaN(precio3) || precio3 < 0) {
      errors.push(
        "El precio de 3 días debe ser un número válido mayor o igual a 0"
      );
      isValid = false;
    }

    // Validar precio 5 días
    const precio5 = parseFloat(document.getElementById("precio_5_dias").value);
    if (isNaN(precio5) || precio5 < 0) {
      errors.push(
        "El precio de 5 días debe ser un número válido mayor o igual a 0"
      );
      isValid = false;
    }

    // Validar deportes disponibles
    const deportes = document
      .getElementById("deportes_disponibles")
      .value.trim();
    if (!deportes || deportes.length < 5) {
      errors.push("Los deportes disponibles deben tener al menos 5 caracteres");
      isValid = false;
    }

    if (!isValid) {
      e.preventDefault();
      alert(
        "Por favor, corrige los siguientes errores:\n\n" + errors.join("\n")
      );
    }
  });
});

  // Confirmación antes de salir con cambios no guardados
  let formChanged = false;
  const form = document.getElementById("form-editar");
if(form){form.addEventListener("input", function () {
    formChanged = true;
  });}
  

window.addEventListener("beforeunload", function (e) {
  if (formChanged) {
    e.preventDefault();
    e.returnValue = "";
  }
});

if(form){  // No mostrar confirmación al enviar el formulario
  form.addEventListener("submit", function () {
    formChanged = false;})}

 
  });
