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
  // updateprice y botones .button-dias
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
        b.classList.remove(
          "activo",
          "bg-[#c4a300]",
          "text-black",
          "opacity-100"
        );
        b.classList.add("inactivo", "bg-gray-600", "text-white", "opacity-70");
      });
      boton.classList.remove(
        "inactivo",
        "bg-gray-600",
        "text-white",
        "opacity-70"
      );
      boton.classList.add(
        "activo",
        "bg-[#c4a300]",
        "text-black",
        "opacity-100"
      );
    });
  });

  // Cambio de imagen según el deporte
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
});
